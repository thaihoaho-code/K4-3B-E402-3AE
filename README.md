# K4-3B-E402-3AE

## Chạy prototype CP3

```powershell
python -m pip install -r codebase/requirements.txt
python codebase/server.py
```

Mở `http://127.0.0.1:5000/`. Cấu hình `GEMINI_API_KEY` trong file `.env` ở thư mục gốc; file này không được commit. Nếu key từng bị lộ trong log/terminal, hãy revoke key cũ và tạo key mới trước khi demo.

## Kiểm tra và đánh giá

```powershell
python -m unittest discover -s codebase -p "test_*.py"
python eval/run_eval.py
python eval/run_eval.py --live
```

`--live` mới gọi Gemini thật. Sau khi hai thành viên chấm output, điền `verdict` và `grader_notes` vào `eval/run1_raw.json`, rồi chạy lại evaluator để tạo `eval/run1_summary.json` và `eval/run1_report.md`.

Evidence live 20 case và pilot 12 input đã được lưu trong `eval/run1_raw.json`, `eval/live_run1_evidence.json` và `eval/pilot_run1.json`. Các phần còn thiếu được ghi rõ, không thay bằng dữ liệu giả: 10 case chatlog thật trong `data/`, chấm độc lập hai reviewer và video demo 30 giây. Xem `eval/pilot_protocol.md` và `eval/demo_script.md`.
