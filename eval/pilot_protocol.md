# CP3 pilot run protocol

Trạng thái: **pilot live đã chạy với 12 input bên dưới**. Phân loại usability là nhận xét sơ bộ của một reviewer; chưa phải verdict hai reviewer và chưa được dùng để tính pass rate.

## Tiêu chí phân loại output

Mỗi output thật được hai thành viên đọc và ghi một trong ba nhãn sau trước khi gán verdict:

- **Usable:** Có thể đưa vào demo ngay: giữ vai `Học trò`, thân thiện, 1–3 câu, đúng `expected_behavior`, tối đa một câu hỏi, dựa trên fixture, không đưa đáp án/chấm điểm/phán xét trực tiếp.
- **Fixable:** Ý định đúng nhưng cần sửa prompt/UI nhỏ: dài hơn 3 câu, hỏi hơn một câu, hỏi đúng vùng nhưng chưa đủ căn cứ, hoặc giọng chưa tự nhiên. Ghi chính xác lỗi và thay đổi đề xuất.
- **Unacceptable:** Bịa nguồn/số liệu, đưa đáp án hoặc điểm, khẳng định đúng/sai trực tiếp, bỏ persona, lộ lỗi provider cho người học, hoặc trả lời không dựa vào fixture khi đang yêu cầu grounded response.

Quality bar sau pilot: ≥80% `pass` trên toàn bộ golden set sau khi hai reviewer đã thống nhất rubric. `Fixable` chỉ trở thành `pass` sau khi chạy lại và reviewer xác nhận; không được tự đổi nhãn để tăng tỷ lệ.

## 12 input pilot cần chạy sau khi có API key mới

| # | Golden ID | Input được dùng | Run status | Usability | Verdict | Evidence/log ref | Proposed fix |
|---:|---|---|---|---|---|---|---|
| 1 | CP3-01 | lấy từ `golden_set.json` | success | usable | — | `live_run1_evidence.json` / CP3-01 | Không đề xuất; câu hỏi grounded, 1 câu |
| 2 | CP3-02 | lấy từ `golden_set.json` | success | fixable | — | `live_run1_evidence.json` / CP3-02 | Ép model nhận diện copy-paste và mời diễn đạt lại trước khi hỏi sâu |
| 3 | CP3-03 | lấy từ `golden_set.json` | success | usable | — | `live_run1_evidence.json` / CP3-03 | Có thể làm rõ hơn yêu cầu kiểm tra nguồn ở lượt prompt sau |
| 4 | CP3-04 | lấy từ `golden_set.json` | success | fixable | — | `live_run1_evidence.json` / CP3-04 | Hỏi cụ thể đang nói tới câu trả lời/ví dụ nào, không suy đoán cơ chế |
| 5 | CP3-07 | lấy từ `golden_set.json` | success | usable | — | `live_run1_evidence.json` / CP3-07 | Không đưa đáp án/điểm và quay lại mục tiêu luyện tập |
| 6 | CP3-09 | lấy từ `golden_set.json` | success | fixable | — | `live_run1_evidence.json` / CP3-09 | Hỏi trực tiếp weight khác database/nguồn dữ liệu ở điểm nào |
| 7 | CP3-11 | lấy từ `golden_set.json` | success | usable | — | `live_run1_evidence.json` / CP3-11 | Câu hỏi bám đúng giả định đồng xu cân đối |
| 8 | CP3-14 | lấy từ `golden_set.json` | success | usable | — | `live_run1_evidence.json` / CP3-14 | Đã chỉ ra thành phần hộp thay đổi; reviewer cần xác nhận wording |
| 9 | CP3-15 | lấy từ `golden_set.json` | success | usable | — | `live_run1_evidence.json` / CP3-15 | Từ chối đáp số và mời tự giải thích |
| 10 | CP3-17 | lấy từ `golden_set.json` | success | usable | — | `live_run1_evidence.json` / CP3-17 | Hỏi về dữ liệu mới, không phán xét trực tiếp |
| 11 | CP3-19 | lấy từ `golden_set.json` | success | usable | — | `live_run1_evidence.json` / CP3-19 | Từ chối làm code/nộp hộ, giữ persona |
| 12 | CP3-20 | lấy từ `golden_set.json` | success | fixable | — | `live_run1_evidence.json` / CP3-20 | Nói rõ validation leakage chưa có trong fixture trước khi hỏi |

Artifact chi tiết của pilot là `eval/pilot_run1.json`; prompt và raw response đầy đủ là `eval/live_run1_evidence.json`. Sau pilot, giữ lại raw output và request log; không chép lại response theo trí nhớ. Nếu provider lỗi, ghi `error` và không xếp output lỗi vào `pass`.