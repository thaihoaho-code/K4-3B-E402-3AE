"""Run and summarise the CP3 golden set without inventing evaluation scores.

Examples (from the repository root):
    python eval/run_eval.py
    python eval/run_eval.py --live

The default command validates the dataset and refreshes the summary from the
existing run1_raw.json. Only --live calls the real model. Human graders add
``verdict`` (pass/fail) and ``grader_notes`` to run1_raw.json, then rerun this
script to obtain the final counts.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CODEBASE = ROOT / "codebase"
EVAL_DIR = ROOT / "eval"
GOLDEN = EVAL_DIR / "golden_set.json"
GRID = EVAL_DIR / "user_input_grid.json"
RAW = EVAL_DIR / "run1_raw.json"
SUMMARY = EVAL_DIR / "run1_summary.json"
REPORT = EVAL_DIR / "run1_report.md"
EVIDENCE = EVAL_DIR / "live_run1_evidence.json"
PILOT = EVAL_DIR / "pilot_run1.json"

sys.path.insert(0, str(CODEBASE))

VALID_VERDICTS = {"pass", "fail"}
TAXONOMY = {
    "source_of_truth",
    "ambiguity_missing_information",
    "out_of_scope_authority",
    "domain_specific",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_dataset(cases: list[dict[str, Any]], grid: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids = [case.get("id") for case in cases]
    if len(cases) < 20:
        errors.append(f"Golden set chỉ có {len(cases)} case; yêu cầu tối thiểu 20.")
    if len(ids) != len(set(ids)):
        errors.append("Golden set có ID trùng nhau.")

    taxonomy_counts = Counter(case.get("taxonomy") for case in cases)
    for taxonomy in TAXONOMY:
        if taxonomy_counts[taxonomy] < 2:
            errors.append(f"Taxonomy {taxonomy} có {taxonomy_counts[taxonomy]} case; yêu cầu tối thiểu 2.")

    common_count = sum(case.get("frequency") == "common" for case in cases)
    rare_count = sum(case.get("frequency") == "rare" for case in cases)
    if common_count < 8 or common_count > 10:
        errors.append(f"Case common={common_count}; yêu cầu 8–10.")
    if rare_count < 2 or rare_count > 4:
        errors.append(f"Case rare={rare_count}; yêu cầu 2–4.")

    assignments = grid.get("case_assignments", {})
    dimensions = set(grid.get("dimensions", {}))
    for case in cases:
        case_id = case.get("id")
        case_grid = case.get("grid", {})
        if set(case_grid) != dimensions:
            errors.append(f"{case_id}: grid không phủ đúng các dimension đã khai báo.")
        if assignments.get(case_id) != case_grid:
            errors.append(f"{case_id}: case_assignments không khớp grid trong golden set.")
        if case.get("taxonomy") not in TAXONOMY:
            errors.append(f"{case_id}: taxonomy không hợp lệ.")
        if not case.get("source_ref") or not case.get("source_type"):
            errors.append(f"{case_id}: thiếu provenance source_type/source_ref.")

    missing_assignments = set(ids) - set(assignments)
    if missing_assignments:
        errors.append(f"User Input Grid thiếu assignment: {sorted(missing_assignments)}.")
    return errors


def blank_result(case: dict[str, Any]) -> dict[str, Any]:
    return {
        **case,
        "model_output": "",
        "run_status": "not_run",
        "error": "",
        "verdict": None,
        "grader_notes": "",
    }


def load_previous_results() -> dict[str, dict[str, Any]]:
    if not RAW.exists():
        return {}
    try:
        previous = read_json(RAW)
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(previous, list):
        return {}
    return {item.get("id"): item for item in previous if isinstance(item, dict) and item.get("id")}


def sync_live_evidence(results: list[dict[str, Any]]) -> None:
    """Copy only auditable fields from ignored technical logs into eval/.

    Matching is by exact student input and latest successful log. Golden-set
    inputs are unique, so this creates a stable case-to-log manifest without
    exposing the API key or depending on terminal output.
    """
    log_records: list[tuple[Path, dict[str, Any]]] = []
    log_dir = ROOT / "logs"
    for path in sorted(log_dir.glob("call_*.json")):
        try:
            record = read_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(record, dict) and record.get("status") == "success":
            log_records.append((path, record))

    evidence: list[dict[str, Any]] = []
    for result in results:
        matches = [
            (path, record)
            for path, record in log_records
            if record.get("input") == result.get("student_input")
        ]
        if not matches:
            continue
        path, record = matches[-1]
        result["model"] = record.get("model", "")
        result["request_id"] = record.get("request_id", "")
        result["log_file"] = str(path.relative_to(ROOT)).replace("\\", "/")
        evidence.append(
            {
                "id": result["id"],
                "status": record.get("status"),
                "model": record.get("model"),
                "request_id": record.get("request_id"),
                "log_file": str(path.relative_to(ROOT)).replace("\\", "/"),
                "input": record.get("input"),
                "prompt_sent": record.get("prompt_sent"),
                "raw_response": record.get("raw_response"),
                "timestamp": record.get("timestamp"),
                "duration_ms": record.get("duration_ms"),
            }
        )

    EVIDENCE.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source": "logs/call_*.json",
                "case_count": len(evidence),
                "records": evidence,
                "secret_policy": "API keys are not copied; provider errors are redacted by ai_core.safe_error.",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def run_live(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # Import only for --live so a dataset-only check does not require SDK/API
    # availability. ask_hoc_tro itself never falls back to a canned response.
    from ai_core import ask_hoc_tro, safe_error

    results: list[dict[str, Any]] = []
    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] Running {case['id']}...")
        result = blank_result(case)
        started = time.perf_counter()
        try:
            result["model_output"] = ask_hoc_tro(
                case["student_input"],
                topic=case.get("topic", ""),
                topic_id=case.get("topic_id", "llm"),
            )
            result["run_status"] = "success"
        except Exception as exc:  # Preserve honest failure evidence per case.
            result["run_status"] = "error"
            result["error"] = f"{type(exc).__name__}: {safe_error(exc)}"
        result["duration_ms"] = round((time.perf_counter() - started) * 1000, 1)
        results.append(result)
    return results


def merge_existing(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    previous = load_previous_results()
    results: list[dict[str, Any]] = []
    for case in cases:
        result = blank_result(case)
        old = previous.get(case["id"], {})
        # Keep only measured output/status and explicit human annotations.
        for key in ("model_output", "run_status", "error", "duration_ms", "verdict", "pass", "grader_notes", "grader"):
            if key in old:
                result[key] = old[key]
        results.append(result)
    return results


def valid_verdict(value: Any) -> str | None:
    if isinstance(value, bool):
        return "pass" if value else "fail"
    if isinstance(value, str) and value.lower() in VALID_VERDICTS:
        return value.lower()
    return None


def result_verdict(result: dict[str, Any]) -> str | None:
    verdict = valid_verdict(result.get("verdict"))
    if verdict is not None:
        return verdict
    return valid_verdict(result.get("pass"))


def independent_grading(results: list[dict[str, Any]]) -> dict[str, Any]:
    comparisons = []
    for result in results:
        grader_a = valid_verdict(result.get("grader_a_verdict"))
        grader_b = valid_verdict(result.get("grader_b_verdict"))
        if grader_a and grader_b:
            comparisons.append(
                {
                    "id": result["id"],
                    "grader_a": grader_a,
                    "grader_b": grader_b,
                    "agree": grader_a == grader_b,
                }
            )
    disagreements = sum(not item["agree"] for item in comparisons)
    return {
        "cases_compared": len(comparisons),
        "disagreements": disagreements,
        "disagreement_rate_percent": round(disagreements / len(comparisons) * 100, 1)
        if comparisons
        else None,
        "rubric_review_required": bool(comparisons and disagreements / len(comparisons) >= 0.2),
        "comparisons": comparisons,
    }


def failure_analysis(results: list[dict[str, Any]]) -> dict[str, Any]:
    failures = [result for result in results if result_verdict(result) == "fail"]
    categories = Counter(
        str(result.get("failure_category") or "uncategorized")
        for result in failures
    )
    return {
        "status": "available" if failures else "no_graded_failures",
        "failure_count": len(failures),
        "categorized_counts": dict(categories),
        "cases": [
            {
                "id": result["id"],
                "failure_category": result.get("failure_category") or "uncategorized",
                "grader_notes": result.get("grader_notes", ""),
            }
            for result in failures
        ],
        "policy": "A failure category is included only when a human grader records it; the evaluator does not infer failures from model text.",
    }


def count_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    status_counts = Counter(result.get("run_status", "not_run") for result in results)
    verdicts = [result_verdict(result) for result in results]
    graded = [verdict for verdict in verdicts if verdict]
    passed = sum(verdict == "pass" for verdict in graded)

    by_taxonomy: dict[str, dict[str, Any]] = {}
    for taxonomy in sorted(TAXONOMY):
        selected = [
            verdicts[index]
            for index, result in enumerate(results)
            if result.get("taxonomy") == taxonomy
        ]
        selected_graded = [verdict for verdict in selected if verdict]
        selected_passed = sum(verdict == "pass" for verdict in selected_graded)
        by_taxonomy[taxonomy] = {
            "total": len(selected),
            "pass": selected_passed,
            "fail": sum(verdict == "fail" for verdict in selected_graded),
            "ungraded": len(selected) - len(selected_graded),
            "pass_rate_among_graded_percent": round(selected_passed / len(selected_graded) * 100, 1)
            if selected_graded
            else None,
        }

    provenance = Counter(result.get("source_type", "unknown") for result in results)
    return {
        "total_cases": total,
        "run_status": {
            "success": status_counts.get("success", 0),
            "error": status_counts.get("error", 0),
            "not_run": status_counts.get("not_run", 0),
        },
        "graded": len(graded),
        "pass": passed,
        "fail": sum(verdict == "fail" for verdict in graded),
        "ungraded": total - len(graded),
        "pass_rate_among_graded_percent": round(passed / len(graded) * 100, 1) if graded else None,
        # Do not display a seemingly authoritative whole-set rate while some
        # cases are ungraded. The graded-case rate above remains available.
        "pass_rate_among_all_cases_percent": round(passed / total * 100, 1)
        if total and len(graded) == total
        else None,
        "by_taxonomy": by_taxonomy,
        "provenance": dict(provenance),
    }


def build_summary(results: list[dict[str, Any]], validation_errors: list[str]) -> dict[str, Any]:
    chatlog_count = sum(
        result.get("source_type") in {"chatlog", "chatlog-derived"}
        for result in results
    )
    counts = count_results(results)
    independent = independent_grading(results)
    evidence = {
        "dataset_structure_valid": not validation_errors,
        "chatlog_provenance_met": chatlog_count >= 10,
        "live_model_run_completed": counts["run_status"]["success"] == len(results),
        "prompt_and_raw_log_evidence_present": EVIDENCE.is_file(),
        "five_case_two_reviewer_check_completed": independent["cases_compared"] >= 5,
        "demo_video_present": any(
            (ROOT / name).is_file()
            for name in ("demo.mp4", "demo.webm", "demo.mov")
        ),
    }
    evidence["submission_ready"] = all(evidence.values())
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_name": "CP3 run 1",
        "measurement_policy": {
            "pass_rate_denominator": "graded cases only",
            "ungraded_cases_count_as_fail": False,
            "scores_are_human_verdicts": True,
            "quality_bar": ">=80% among graded cases after rubric alignment",
        },
        "dataset_validation": {
            "structure_valid": not validation_errors,
            "submission_requirements_complete": evidence["submission_ready"],
            "errors": validation_errors,
            "chatlog_provenance": {
                "case_count": chatlog_count,
                "minimum_required": 10,
                "met": chatlog_count >= 10,
                "data_directory_present": (ROOT / "data").is_dir(),
            },
        },
        "counts": counts,
        "independent_grading": independent,
        "failure_analysis": failure_analysis(results),
        "evidence_checklist": evidence,
    }


def report_line(result: dict[str, Any]) -> str:
    verdict = result_verdict(result) or "ungraded"
    note = str(result.get("grader_notes") or "").strip()
    output = str(result.get("model_output") or "").strip().replace("\n", " ")
    error = str(result.get("error") or "").strip()
    detail = note or error or (f"output: {output}" if output else "chưa có output")
    detail = detail.replace("|", "\\|")
    return f"| {result['id']} | {result.get('taxonomy', '')} | {result.get('run_status', 'not_run')} | {verdict} | {detail} |"


def write_report(summary: dict[str, Any], results: list[dict[str, Any]]) -> None:
    counts = summary["counts"]
    lines = [
        "# CP3 — kết quả kiểm thử lượt 1",
        "",
        f"> Sinh lúc: `{summary['generated_at']}`. Đây là số đo từ file output, không phải số liệu ước đoán.",
        "",
        "## Bảng thống kê",
        "",
        "| Chỉ số | Giá trị |",
        "|---|---:|",
        f"| Tổng số case | {counts['total_cases']} |",
        f"| Model trả output thành công | {counts['run_status']['success']} |",
        f"| Lỗi khi chạy | {counts['run_status']['error']} |",
        f"| Chưa chạy | {counts['run_status']['not_run']} |",
        f"| Đã chấm | {counts['graded']} |",
        f"| Đạt | {counts['pass']} |",
        f"| Không đạt | {counts['fail']} |",
        f"| Chưa chấm | {counts['ungraded']} |",
        f"| Tỷ lệ đạt / case đã chấm | {counts['pass_rate_among_graded_percent'] if counts['pass_rate_among_graded_percent'] is not None else 'N/A'}% |",
        f"| Cấu trúc dataset hợp lệ | {'Có' if summary['dataset_validation']['structure_valid'] else 'Không'} |",
        f"| Đủ provenance 10 chatlog thật | {'Có' if summary['dataset_validation']['chatlog_provenance']['met'] else 'Không'} |",
        f"| Đủ điều kiện submission hiện tại | {'Có' if summary['dataset_validation']['submission_requirements_complete'] else 'Không'} |",
        f"| Đã hoàn tất live model run | {'Có' if summary['evidence_checklist']['live_model_run_completed'] else 'Không'} |",
        f"| Có manifest prompt/raw response để audit | {'Có' if summary['evidence_checklist']['prompt_and_raw_log_evidence_present'] else 'Không'} |",
        f"| Đã chấm độc lập 5 case | {'Có' if summary['evidence_checklist']['five_case_two_reviewer_check_completed'] else 'Không'} |",
        f"| Đã có video demo | {'Có' if summary['evidence_checklist']['demo_video_present'] else 'Không'} |",
        f"| Tỷ lệ đạt / toàn bộ case | {counts['pass_rate_among_all_cases_percent'] if counts['pass_rate_among_all_cases_percent'] is not None else 'N/A'} |",
        "",
        "## Theo taxonomy",
        "",
        "| Taxonomy | Tổng | Đạt | Không đạt | Chưa chấm | Tỷ lệ đạt trên case đã chấm |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for taxonomy, item in counts["by_taxonomy"].items():
        rate = item["pass_rate_among_graded_percent"]
        lines.append(f"| {taxonomy} | {item['total']} | {item['pass']} | {item['fail']} | {item['ungraded']} | {rate if rate is not None else 'N/A'}% |")

    lines.extend(
        [
            "",
            "## Phân tích từng case",
            "",
            "| ID | Taxonomy | Chạy | Verdict | Nguyên nhân/ghi chú |",
            "|---|---|---|---|---|",
        ]
    )
    lines.extend(report_line(result) for result in results)
    lines.extend(
        [
            "",
            "## Cảnh báo tính trung thực",
            "",
            "- Case chưa có `verdict` không được tính là đạt cũng không tự động tính là thất bại.",
            "- `source_type` hiện được lấy nguyên từ golden set. Nếu là `spec-derived` thì không được báo cáo là chatlog thật.",
            "- Yêu cầu tối thiểu 10 case từ chatlog trong `data/` chưa đạt nếu summary ghi `chatlog_provenance.met=false`.",
            "- Quality bar ≥80% là ngưỡng đề xuất sau khi hai người chấm thống nhất rubric, không phải kết luận sản phẩm đã đạt.",
        ]
    )
    independent = summary["independent_grading"]
    lines.extend(
        [
            "",
            "## Pilot usability (sơ bộ)",
            "",
            "- Artifact: `eval/pilot_run1.json`.",
            "- Đây là phân loại của 1 reviewer trên 12 output, không phải pass/fail cuối và không được dùng làm tỷ lệ đạt.",
        ]
    )
    if PILOT.exists():
        try:
            pilot = read_json(PILOT)
            pilot_summary = pilot.get("summary", {})
            lines.append(
                f"- Kết quả sơ bộ: usable={pilot_summary.get('usable', 0)}, fixable={pilot_summary.get('fixable', 0)}, unacceptable={pilot_summary.get('unacceptable', 0)}."
            )
        except (OSError, json.JSONDecodeError):
            lines.append("- Không đọc được pilot_run1.json.")
    lines.extend(
        [
            "",
            "## Chấm độc lập 5 case",
            "",
            f"- Số case đã có verdict từ cả hai reviewer: {independent['cases_compared']}.",
            f"- Số bất đồng: {independent['disagreements']}.",
            f"- Tỷ lệ bất đồng: {independent['disagreement_rate_percent'] if independent['disagreement_rate_percent'] is not None else 'N/A'}%.",
            f"- Cần xem lại rubric: {'Có' if independent['rubric_review_required'] else 'Chưa có đủ bằng chứng/không vượt ngưỡng'}.",
            "- Template điền độc lập: `eval/grading_template.json`; các verdict phải được ghi vào raw artifact trước khi tính.",
            "",
            "## Phân tích failure",
            "",
        ]
    )
    failure_summary = summary["failure_analysis"]
    if failure_summary["failure_count"]:
        lines.append(f"- Có {failure_summary['failure_count']} case fail do reviewer ghi nhận.")
        for category, count in failure_summary["categorized_counts"].items():
            lines.append(f"- `{category}`: {count} case.")
    else:
        lines.append("- Chưa có case fail đã được reviewer chấm; không thể tạo failure analysis empirical.")
    chatlog = summary["dataset_validation"]["chatlog_provenance"]
    if not chatlog["met"]:
        lines.extend(
            [
                "",
                "## Thiếu provenance chatlog",
                "",
                f"- Mới có {chatlog['case_count']}/{chatlog['minimum_required']} case có `source_type` chatlog.",
                "- Repository chưa có `data/`; cần bổ sung chatlog thật và cập nhật `source_ref` trước khi nộp CP3.",
            ]
        )
    if summary["dataset_validation"]["errors"]:
        lines.extend(["", "## Lỗi cấu trúc dataset", ""])
        lines.extend(f"- {error}" for error in summary["dataset_validation"]["errors"])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Call the real Gemini model for every case.")
    args = parser.parse_args()

    try:
        cases = read_json(GOLDEN)
        grid = read_json(GRID)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Không đọc được dataset: {exc}", file=sys.stderr)
        return 2
    if not isinstance(cases, list) or not isinstance(grid, dict):
        print("golden_set.json hoặc user_input_grid.json sai kiểu dữ liệu.", file=sys.stderr)
        return 2

    validation_errors = validate_dataset(cases, grid)
    if validation_errors:
        print("Dataset validation FAILED:")
        for error in validation_errors:
            print(f"- {error}")
        return 2

    results = run_live(cases) if args.live else merge_existing(cases)
    sync_live_evidence(results)
    RAW.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = build_summary(results, validation_errors)
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(summary, results)

    counts = summary["counts"]
    print(f"Đã ghi {RAW}, {SUMMARY} và {REPORT}.")
    print(
        "Tổng: {total}; đạt: {passed}; thất bại: {failed}; chưa chấm: {ungraded}; tỷ lệ đạt trên case đã chấm: {rate}".format(
            total=counts["total_cases"],
            passed=counts["pass"],
            failed=counts["fail"],
            ungraded=counts["ungraded"],
            rate=(f"{counts['pass_rate_among_graded_percent']}%" if counts["pass_rate_among_graded_percent"] is not None else "N/A"),
        )
    )
    if not args.live:
        print("Chưa gọi model. Dùng --live sau khi có API key mới và cấu hình GEMINI_API_KEY.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())