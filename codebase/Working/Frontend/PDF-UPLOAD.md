# Upload slide PDF — frontend

## Cài đặt

Trong `codebase/Working/Frontend`, chạy `npm install` (PowerShell có thể dùng `npm.cmd install`). Package đã khai báo `pdfjs-dist` và Playwright cho test. Dùng Node >=22.13 hoặc >=24, phù hợp phiên bản pdf.js đã khóa trong lockfile.

Script `postinstall` sao chép thư viện, worker, CMaps, standard fonts và WASM từ `node_modules/pdfjs-dist` sang `vendor/pdfjs`. Đây là tài nguyên sinh tự động, không commit. Nếu cài với `--ignore-scripts`, chạy thêm `node scripts/copy-pdfjs.cjs`. Khi deploy phải mang theo thư mục `vendor/pdfjs` đã sinh.

Frontend tiếp tục được phục vụ bởi static mount hiện có. Không thay đổi FastAPI. Mở bằng HTTP từ server hiện tại, không mở bằng `file://`.

## Trích xuất và gửi dữ liệu

`pdf-upload.js` cung cấp `async function extractPdfSlides(file)`; tham số tùy chọn hỗ trợ hủy và tiến độ. Module pdf.js được import khi cần. `GlobalWorkerOptions.workerSrc` trỏ đến `vendor/pdfjs/pdf.worker.mjs`, cùng phiên bản với `pdf.mjs`, cùng origin. Đọc từng trang bằng `getPage()` và `getTextContent()`, ghép `item.str` theo thứ tự, giữ Unicode, xử lý tuần tự và nhường event loop giữa các trang. Luồng document/page theo [tài liệu PDF.js](https://mozilla.github.io/pdf.js/examples/).

Ví dụ JSON trả về và POST:

```json
{
  "title": "AI_Training_Process.pdf",
  "slides": [
    { "slide_ref": "Slide 1", "text": "Giới thiệu về mô hình ngôn ngữ." },
    { "slide_ref": "Slide 2", "text": "" }
  ]
}
```

Hằng `UPLOAD_TOPIC_ENDPOINT` trong `app.js` mặc định là `/topics/from-slides`. Request dùng POST, `Content-Type: application/json`, không multipart. Backend cần cung cấp endpoint này hoặc đổi hằng sang endpoint JSON tương thích đã có. Frontend không tạo endpoint và không giả lập thành công khi server chưa hỗ trợ.

Response hỗ trợ `{ "topic": { "topic_id": "...", "title": "...", "slides": [...] } }` hoặc object topic trực tiếp; chấp nhận `id` thay cho `topic_id`. Slide cần `slide_ref` và `text`. ID trùng bị từ chối để không ghi đè topic cũ. Thiếu ID thì dùng hash ổn định từ tên file và hiện cảnh báo: đó chỉ là fallback frontend, backend có thể không nhận ID này khi gọi `/chat`.

Chỉ sau khi response hợp lệ mới thêm vào catalog, render sidebar và gọi `start(topic)`. Lỗi đọc, HTTP, JSON hay schema không xóa topic/lịch sử đang có. Chọn file mới hủy tác vụ cũ. Topic upload nằm trong bộ nhớ trang; tải lại trang không khôi phục topic này. Nội dung chỉ hiển thị bằng DOM/textContent.

## Giới hạn

- Chỉ MIME `application/pdf`, tối đa 20 MiB (20 × 1024 × 1024 byte), 100 trang, 1.000.000 ký tự kể cả khoảng phân cách trong khi trích xuất.
- Trang trống vẫn có `text: ""`. PDF không có text ở mọi trang bị từ chối, không POST. Không OCR, không hỗ trợ PDF dạng ảnh hoặc PDF khóa mật khẩu.
- Thứ tự đọc phụ thuộc text layer PDF; tài liệu nhiều cột hoặc font không có ánh xạ Unicode đúng có thể trích xuất không như bố cục nhìn thấy.
- Tác vụ quá 90 giây được hủy và cho phép thử lại.
- Không gửi file PDF, không dùng localStorage cho PDF, không sửa corpus và không chứa API key. Chỉ gửi JSON văn bản đến endpoint đã cấu hình.

## Kiểm thử

Từ `codebase/Working`:

```sh
node --check Frontend/app.js
node --check Frontend/pdf-upload.js
node tests/frontend.cjs
```

Bộ test dùng Edge headless đã cài trên máy (`BROWSER_CHANNEL` có thể đổi sang `chrome`) và HTTP server chỉ dành cho test, không gọi backend thật. Fixture PDF thật có ToUnicode kiểm tra tiếng Việt, nhiều trang/trang trống, giới hạn trang, MIME/dung lượng, schema request, hai dạng response, fallback ID, lỗi giữ phiên, hủy request cũ, render an toàn và mobile 320/390/768px. Đồng thời chạy lại SSE, skip, reference, notes và corpus retry.
