# Đánh giá Học trò

Quy trình kiểm thử trong eval.py gồm 4 bước:

1. **Chuẩn bị đầu vào:** Đọc 22 case trong golden set, mỗi case có câu người dùng, lịch sử hội thoại, slide liên quan và khoảng trống cần hỏi.
2. **Sinh phản hồi:** Đưa đầu vào qua `build_prompt` rồi gọi model đóng vai “Học trò”. Không gửi đáp án mẫu hay tiêu chí chấm cho model này.
3. **Chấm theo rubric:** Dùng một LLM judge đánh giá phản hồi có đúng vai, chỉ hỏi một câu chính, bám slide, không giải hộ hoặc chấm đúng/sai. Mỗi tiêu chí có kết quả và lý do.
4. **Tổng hợp và rà soát:** Lưu kết quả từng case, tính tỷ lệ PASS và xem lỗi theo nhóm. Nhóm kiểm tra lại nhận xét của judge; mục tiêu là ít nhất **19/22 case đạt**, với toàn bộ case đã được chấm đầy đủ.

`eval.py` chạy golden set qua `build_prompt`, dùng LLM judge chấm từng rubric. Kiểm thử bước sinh câu hỏi với slide/lịch sử có sẵn, chưa đánh giá retrieval qua `/chat`.

## Chuẩn bị

Đặt cùng thư mục: `eval.py`, `golden_set.json` bản mới, `prompt.py`, `slide_corpus.json`, `tutor_turns.csv`. Dùng Python 3.10+.

```powershell
python -m pip install httpx
```

## Chạy

Trong PowerShell, thay các giá trị bên dưới bằng API key và tên model thực tế:

```powershell
$env:GEMINI_API_KEY = "KEY_CUA_BAN"
python eval.py --chatlog tutor_turns.csv --model "MODEL_CUA_BAN" --judge-model "MODEL_CHAM"
```

Script không tự đọc `.env`. Không cần bật FastAPI. Một lượt đủ 22 case thường gọi API 44 lần, gồm sinh phản hồi và chấm.

Kiểm tra dữ liệu, không gọi API:

```powershell
python eval.py --chatlog tutor_turns.csv --validate-only
```

Thêm `--ids G01,G02` vào lệnh chạy để thử hai case.

## Kết quả

Xem `eval_results.json`: phản hồi, lý do chấm từng tiêu chí và thống kê theo nhóm.

- **PASS / FAIL:** đạt toàn bộ rubric / có tiêu chí không đạt.
- **PENDING:** cần người chấm xem lại.
- **ERROR / NOT_RUN:** lỗi API hoặc chưa chạy; không tính PASS.

Ngưỡng mặc định 85% (ít nhất 19/22), chỉ đạt khi tất cả case đã được chấm PASS/FAIL. Exit code: `0` đạt, `1` dưới ngưỡng, `2` lỗi hoặc chưa chấm đủ. Điểm LLM judge cần được đối chiếu với người chấm.
