# Bàn giao frontend — Nguyễn Đình Lâm Phúc

Frontend phát triển từ `Mock/app.js`, giữ nguyên từng byte của `index.html` (từ `Mock/Mock.html`) và `style.css`. Nội dung nhãn mô phỏng được cập nhật bằng JS; nút tạo phản hồi giả được ẩn. Không sửa phần Python, prompt, validator, dữ liệu hay eval của thành viên khác.

## Đã thực hiện

- Bỏ `topics[]`, `references`, `getReply()`, `questionReply()` và phản hồi bằng timer.
- Tải chủ đề và nội dung slide từ `/data/slide_corpus.json`; không dùng dữ liệu mock dự phòng trong sản phẩm. Thiếu dữ liệu thì báo lỗi, khóa gửi và cho thử lại bằng **Buổi học mới**.
- `sendMessage(text)` gửi JSON tới `/chat`, đọc `response.body.getReader()` bằng `TextDecoder` streaming. Hỗ trợ event bị chia qua nhiều chunk, UTF-8 tiếng Việt, LF/CRLF/CR, comment heartbeat, nhiều dòng `data:`, `[DONE]`, `done: true` và `event: done`.
- Ghép token vào một bubble, khóa composer/Skip/Kết thúc và hiển thị spinner trong lúc chờ. Kiểm tra lời giải thích dài hơn 20 ký tự.
- SourceBadge dùng chính `slide_ref` từ SSE và mở đúng nội dung tương ứng. Không tự thay bằng slide khác khi nguồn không tồn tại.
- Skip gửi `action: "skip"`, `asked_indexes`, history và `user_text: ""` để đáp ứng `ChatRequest` hiện tại; giữ bản nháp.
- Kết thúc mở SummaryDialog; **Lưu ghi chú** POST `/notes` với `{topic_id, turns, reflection}`. Chỉ hiện **Đã lưu ✓** khi HTTP thành công và JSON có `saved: true`. Không lưu localStorage.
- Hủy request khi đổi chủ đề/reset, timeout khi luồng không tiến triển trong 60 giây, khôi phục bản nháp khi lỗi. Chỉ đưa lượt thành công vào history và bộ đếm.

## Hợp đồng tích hợp cần thống nhất khi merge

`models.py` hiện đã xác định request chat/notes, nhưng chưa xác định schema corpus, schema history hoặc metadata chỉ số câu hỏi. Frontend dùng hợp đồng sau; cần đối chiếu với dữ liệu/backend thực tế khi merge.

`GET /data/slide_corpus.json` trả mảng chủ đề:

```json
[
  {
    "topic_id": "course-topic-id",
    "title": "Tên chủ đề từ tài liệu",
    "slides": [
      { "slide_ref": "Slide 15", "text": "Nội dung slide từ corpus" }
    ]
  }
]
```

Cũng nhận `id` thay `topic_id`, `topic_title` thay `title`, `content` thay `text`. Mã chủ đề phải duy nhất; `slide_ref` phải khớp giữa corpus và SSE.

`POST /chat` nhận `history` là mảng `{role: "user" | "assistant", content: string}` của các lượt trước đã hoàn tất. Lời giải thích mới nằm trong `user_text`, không lặp lại trong history. Backend chuyển role sang định dạng SDK của mình nếu cần.

Response phải có `Content-Type: text/event-stream`, mỗi event kết thúc bằng dòng trống:

```text
data: {"text":"Thầy/cô ơi, "}

data: {"text":"hãy giải thích thêm nhé?"}

data: {"slide_ref":"Slide 15","asked_index":0}

data: [DONE]

```

`text` là phần văn bản tăng thêm, không phải toàn bộ câu trả lời lặp lại. `slide_ref` có thể đi cùng token hoặc trong event riêng. Có thể kết thúc bằng EOF sau event đầy đủ; event bị cắt dở bị coi là lỗi. Nếu mất kết nối đúng ranh giới event mà không có dấu kết thúc, FE không thể phân biệt EOF bình thường và lỗi; backend nên gửi `[DONE]` để chốt luồng.

Backend gửi `asked_index` (số nguyên không âm) hoặc `asked_indexes` (mảng) để frontend tích lũy và gửi lại khi Skip. `ChatResponse` hiện chỉ có `text`/`slide_ref`, nên backend cần bổ sung metadata này nếu dùng chỉ số chống lặp; frontend không suy đoán chỉ số câu hỏi từ số slide. Khi chưa có metadata, mảng gửi đi là `[]`, backend vẫn nhận toàn bộ history.

Lỗi sau khi bắt đầu SSE có thể gửi `event: error` kèm `data: {"error":"Thông báo"}`. `/notes` phải thật sự lưu dữ liệu trước khi trả `{"saved":true}`.

## Chạy với backend sau merge

Chạy từ `codebase/Working` vì `main.py` mount static theo thư mục hiện tại:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Mở `http://localhost:8000`; không mở HTML bằng `file://`. Cần corpus và cấu hình backend thực tế của nhóm.

## Kiểm chứng đã chạy

`node --check app.js` và `tests/frontend.cjs` đều thành công. Test dùng Edge headless với HTTP server SSE riêng, có độ trễ và chia từng byte thật qua mạng cục bộ; không sửa backend hay ghi dữ liệu sản phẩm.

Chạy lại từ `codebase/Working` (Node.js và Edge đã cài):

```powershell
npm.cmd install --prefix tests --no-save --package-lock=false playwright@1.63.0
node tests/frontend.cjs
```

Nếu dùng Chrome: đặt `$env:BROWSER_CHANNEL='chrome'` trước lệnh test. Thư viện này chỉ phục vụ kiểm thử, sản phẩm vẫn là HTML/CSS/JS thuần.

Các ca đã qua: tải chủ đề động; token hiển thị trước khi stream kết thúc; UTF-8/CRLF và data nhiều dòng; pending controls; Slide 15 chính xác; Skip giữ bản nháp, gửi history/indexes; notes lỗi rồi thử lại thành công; HTTP 503; backend trả JSON thay SSE; event bị cắt dở; SSE error; đổi chủ đề hủy luồng; nguồn chưa có; màn hình 390px không tràn ngang; corpus 404 rồi thử lại. Không có lỗi JavaScript trên trình duyệt.

## Gate còn chờ phần việc của nhóm

Chưa thể xác nhận happy path với BE/AI thật: `chat.py` vẫn `pass`, `notes.py` trả thành công giả mà chưa lưu, và chưa có `data/slide_corpus.json`. Không đánh dấu gate E2E thật là hoàn tất.

Sau merge cần kiểm thử tay: gửi giải thích và thấy Gemini stream; mở badge đúng slide; thử yêu cầu đáp án/copy-paste để kiểm tra guard BE; Skip có câu hỏi mới; lưu ghi chú và kiểm tra dữ liệu tồn tại ở backend; đổi chủ đề/reset giữa luồng. Đây là kiểm chứng tích hợp, không mở rộng phạm vi frontend sang triển khai backend/eval.
