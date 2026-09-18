import json
import os
from pathlib import Path
from typing import Any

import httpx


BASE_URL = os.getenv("EVAL_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
GOLDEN_PATH = Path(__file__).with_name("golden_set.json")
VALID_EXPECT_TYPES = {"question", "statement", "request"}


def load_cases() -> list[dict]:
    with GOLDEN_PATH.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list) or not cases:
        raise ValueError("golden_set.json phải là một mảng không rỗng")

    seen_ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Mỗi golden case phải là object JSON")

        case_id = case.get("id")
        expect_type = case.get("expect_type")

        if not isinstance(case_id, str) or not case_id:
            raise ValueError("Golden case thiếu id hợp lệ")
        if case_id in seen_ids:
            raise ValueError(f"Golden case trùng id: {case_id}")
        if expect_type not in VALID_EXPECT_TYPES:
            raise ValueError(
                f"{case_id}: expect_type phải thuộc {sorted(VALID_EXPECT_TYPES)}"
            )
        if not isinstance(case.get("topic_id"), str) or not case["topic_id"]:
            raise ValueError(f"{case_id}: thiếu topic_id")
        if not isinstance(case.get("user_text"), str) or not case["user_text"].strip():
            raise ValueError(f"{case_id}: thiếu user_text")

        seen_ids.add(case_id)

    return cases


def call_chat(case: dict) -> tuple[str, str | None]:
    payload = {
        "topic_id": case["topic_id"],
        "user_text": case["user_text"],
        "history": [],
    }

    response = httpx.post(
        f"{BASE_URL}/chat",
        json=payload,
        timeout=30.0,
    )
    response.raise_for_status()

    text_parts: list[str] = []
    slide_ref: str | None = None

    # Backend trả Server-Sent Events:
    #
    # data: {"text": "...", "slide_ref": "Slide 10"}
    # data: {"text": "..."}
    # data: [DONE]
    #
    # Ta gom các chunk text thành một câu trả lời hoàn chỉnh.

    for line in response.text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue

        raw_data = line.removeprefix("data:").strip()

        if raw_data == "[DONE]":
            continue

        try:
            event = json.loads(raw_data)
        except json.JSONDecodeError:
            continue

        if not isinstance(event, dict):
            continue

        if event.get("text"):
            text_parts.append(str(event["text"]))

        if event.get("slide_ref"):
            slide_ref = str(event["slide_ref"])

    return "".join(text_parts), slide_ref


def matches_case(
    case: dict,
    text: str,
    slide_ref: str | None,
) -> bool:
    """
    Kiểm tra output của model có đáp ứng golden case hay không.

    Không exact-match câu trả lời vì Gemini có thể diễn đạt
    cùng một ý theo nhiều cách khác nhau.
    """

    if not text.strip():
        return False

    observed = f"{text} {slide_ref or ''}".casefold()

    # --------------------------------------------------------
    # 1. Required terms
    # --------------------------------------------------------

    required_terms = case.get("must_contain_any", [])

    if required_terms:
        if not any(
            isinstance(term, str)
            and term.strip()
            and term.casefold() in observed
            for term in required_terms
        ):
            return False

    # --------------------------------------------------------
    # 2. Forbidden terms
    # --------------------------------------------------------

    forbidden_terms = case.get("must_not_contain", [])

    if any(
        isinstance(term, str)
        and term.strip()
        and term.casefold() in observed
        for term in forbidden_terms
    ):
        return False

    # --------------------------------------------------------
    # 3. Slide requirement
    # --------------------------------------------------------

    required_slide = case.get("require_slide")

    if required_slide:
        if not slide_ref:
            return False

        if slide_ref.strip().casefold() != required_slide.strip().casefold():
            return False

    return True


def run_eval() -> None:
    cases = load_cases()

    if not cases:
        print("ERROR: golden_set.json không có test case.")
        raise SystemExit(1)

    passed = 0

    print(f"Running {len(cases)} golden cases...")
    print(f"Backend: {BASE_URL}\n")

    for case in cases:
        try:
            text, slide_ref = call_chat(case)

            success = matches_case(
                case,
                text,
                slide_ref,
            )

            error_message = None

        except httpx.ConnectError:
            success = False
            text = ""
            slide_ref = None
            error_message = (
                "Không kết nối được FastAPI. "
                "Hãy chạy: uvicorn main:app --reload"
            )

        except Exception as error:
            success = False
            text = ""
            slide_ref = None
            error_message = str(error)

        if success:
            passed += 1

        status = "PASS" if success else "FAIL"

        print(
            f"[{status}] "
            f"{case['id']} "
            f"type={case['expect_type']} "
            f"note={case.get('note', 'uncategorized')} "
            f"slide={slide_ref} "
            f"reply={text[:120]!r}"
        )

        if error_message:
            print(f"       error={error_message}")

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    total = len(cases)
    percentage = passed / total * 100

    print("\n" + "=" * 50)
    print(f"Result: {passed}/{total} ({percentage:.1f}%)")
    print("=" * 50)

    # Sprint target: >= 85%
    if percentage < 85:
        raise SystemExit(1)


if __name__ == "__main__":
    run_eval()
