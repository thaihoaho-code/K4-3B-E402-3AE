# Kịch bản demo real-time 30 giây

Trạng thái: **chưa quay**. Đây là checklist quay, không phải video đã nộp.

1. **0–5 giây:** Mở `http://127.0.0.1:5000/`, chọn chủ đề “Vì sao mô hình ngôn ngữ có thể bịa?”. Giữ visible dòng “AI thật” và “không chấm điểm”.
2. **5–12 giây:** Bấm “Thử một lời giải thích mẫu”, gửi: `LLM bịa chỉ vì thiếu dữ liệu; có thật nhiều dữ liệu thì luôn đúng.`
3. **12–22 giây:** Hiển thị phản hồi model thật: một câu hỏi ngây thơ xoáy vào sự khác nhau giữa câu trôi chảy và sự thật. Không chỉnh sửa output trên video.
4. **22–27 giây:** Bấm “Gửi input ngoài tài liệu”; cho thấy model được yêu cầu thu hẹp phạm vi thay vì bịa citation.
5. **27–30 giây:** Mở nhanh `/health` hoặc terminal log để chứng minh có model name, request và raw response. Không để API key xuất hiện trên màn hình.

Trước khi quay: revoke key đã từng xuất hiện trong terminal, tạo key mới, chạy server bằng key mới, kiểm tra `logs/` và quay một lần liên tục có timestamp.