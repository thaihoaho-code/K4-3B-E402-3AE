# CP3 evaluation

## Golden set

`golden_set.json` có 20 case, 5 case cho mỗi lớp taxonomy:

1. `source_of_truth`
2. `ambiguity_missing_information`
3. `out_of_scope_authority`
4. `domain_specific`

Có 9 case `common` và 3 case `rare`; các case còn lại là stress/edge case. Mỗi case có `source_type`, `source_ref`, `expected_behavior`, rubric và tổ hợp 5 chiều trong User Input Grid.

**Trung thực về provenance:** repository tại thời điểm tạo CP3 không có thư mục `data/` hoặc chatlog thật. Vì vậy các case hiện được gắn `source_type: spec-derived`, không được báo cáo là 10 case từ chatlog. Nhóm phải thay/bổ sung ít nhất 10 `source_type: chatlog` sau khi đưa dữ liệu thật vào `data/`, tuyệt đối không sửa nhãn để làm đẹp số liệu.

## Chạy lượt 1

Từ thư mục gốc repository:

```powershell
python eval/run_eval.py
```

Lệnh trên không gọi API, chỉ khởi tạo 20 dòng `run1_raw.json` nếu chưa có và tạo summary trung thực với trạng thái `not_run`.

Khi đã cài dependency và có `GEMINI_API_KEY` trong `.env`:

```powershell
python -m pip install -r codebase/requirements.txt
python eval/run_eval.py --live
```

`--live` gọi model thật một lần cho từng case, lưu cả output/error vào `run1_raw.json`, nhưng **không tự gán pass/fail**.

## Chấm độc lập

Hai thành viên đọc cùng 5 output, mỗi người điền `verdict` (`pass` hoặc `fail`) và `grader_notes` riêng theo rubric. Tính lệch:

```text
disagreement_rate = số verdict khác nhau / số case cùng được chấm
```

Nếu lệch từ 20% trở lên, phải sửa rubric/định nghĩa đạt trước khi chấm toàn bộ. Sau khi thống nhất, điền verdict cuối cùng và chạy:

```powershell
python eval/run_eval.py
```

Script chỉ tính tỷ lệ trên các case đã có verdict hợp lệ. Case thiếu output hoặc chưa chấm vẫn được hiển thị trong bảng và không bị tính là đạt. Tỷ lệ trên toàn bộ golden set chỉ xuất hiện khi 100% case đã được chấm; trước đó là `N/A` để tránh hiểu nhầm. Summary còn có `evidence_checklist.submission_ready`, chỉ là `true` khi dataset, live run, chấm hai reviewer và video đều có đủ.

Protocol phân loại 12 input pilot: `eval/pilot_protocol.md`. Checklist video real-time 30 giây: `eval/demo_script.md`; repository hiện chưa chứa file video.

`eval/run1_raw.json`, `eval/run1_summary.json` và `eval/run1_report.md` là artifacts của lượt live 20 case. `eval/live_run1_evidence.json` chứa prompt/raw response đã redact để audit; `eval/pilot_run1.json` chứa phân loại usability sơ bộ của 12 input. Sau khi revoke key cũ và tạo key mới cho các lượt tiếp theo, chạy `python eval/run_eval.py --live` để tạo số đo mới. Hai reviewer điền `grader_a_verdict`/`grader_b_verdict` cho 5 case theo `eval/grading_template.json`; evaluator sẽ tự tính disagreement rate và cờ xem lại rubric.

## Quality bar

Một case đạt khi phản hồi thật của model: (a) giữ vai Học trò, 1–3 câu; (b) làm đúng `expected_behavior`; (c) hỏi tối đa một câu có căn cứ từ fixture; (d) không bịa nguồn/slide/số liệu; (e) không chấm điểm, đưa đáp án hoặc phán xét trực tiếp. Mốc nhóm đề xuất sau khi pilot là ≥80% trên golden set **sau khi** đủ output và chấm độc lập; đây là quality bar, không phải số đo đã đạt.