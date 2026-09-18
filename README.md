# VLearn · Học trò

Bản mock tương tác dựa trên `canvas.md`: học viên giảng lại khái niệm, bot đóng vai học trò và hỏi ngược từng câu, không chấm điểm.

## Cách chạy

Mở `index.html` trực tiếp bằng Chrome, Edge hoặc Firefox. Không cần cài thư viện, backend hay API key. Font Google cần mạng; nếu offline, giao diện dùng font hệ thống.

## Thử trải nghiệm

1. Chọn một trong ba chủ đề ở thanh bên.
2. Nhấn **Thử một lời giải thích mẫu**, rồi gửi bằng nút mũi tên hoặc Enter. Shift + Enter để xuống dòng.
3. Đọc câu hỏi ngược và gửi lời giải thích tiếp theo.
4. Mở **Xem tài liệu mẫu** nếu cần tự tra cứu.
5. Chọn **Kết thúc & ghi lại điều đã học** để lưu ghi chú theo chủ đề vào trình duyệt.
6. **Buổi học mới** hoặc đổi chủ đề sẽ bắt đầu hội thoại mới. Ghi chú đã lưu vẫn được giữ.

## Phạm vi mô phỏng

- Phản hồi dựa trên từ khóa và kịch bản cố định, chưa có LLM, RAG hoặc khả năng đánh giá kiến thức thực tế.
- Tài liệu là nội dung mẫu được biên soạn sẵn.
- Các bước và số lượt thể hiện hoạt động, không phải điểm hay mức độ hiểu bài.
- Hội thoại chỉ tồn tại trong phiên trang hiện tại; ghi chú lưu bằng localStorage nếu trình duyệt cho phép. Không gửi nội dung hội thoại tới máy chủ.
- Giao diện hỗ trợ máy tính và điện thoại.

## Tệp

- `index.html`: bố cục và hộp thoại.
- `style.css`: giao diện responsive.
- `app.js`: chủ đề, hội thoại mô phỏng và lưu ghi chú.

Kiểm tra cú pháp JavaScript: `node --check app.js`.
