**1. Track + đề:**

D3 · VLearn — tính năng mới: Agent "Học trò", học viên dạy lại khái niệm để kiểm chứng độ hiểu sâu.

**2. Job executor:**

Học viên vừa đọc/xem xong một khái niệm lý thuyết cốt lõi trên VLearn, chuẩn bị làm bài tập hoặc thi.

**3. Pain:**

Học xong có cảm giác đã hiểu nhưng khi ứng dụng mới phát hiện hổng kiến thức; muốn giảng lại cho người khác để nhớ lâu nhưng người nghe không đủ chuyên môn để bắt lỗi hoặc không biết cách đặt câu hỏi vặn ngược.

**4. Bằng chứng đầu:**

* Khảo sát 20 học viên: 8/20 (40%) bế tắc lớn nhất là "học xong tưởng hiểu, làm bài mới thấy hổng".
* Khi thử giải thích cho bạn bè, 11/20 (55%) gặp rào cản người nghe không đủ chuyên môn để bắt lỗi; 5/20 (25%) nói người nghe không biết đặt câu hỏi ngược. Nguồn: Sheet khảo sát, 20 mẫu.
* Về phản ứng của AI: 13/20 (65%) yêu cầu AI khi thấy lỗi sai phải đặt "câu hỏi ngây thơ xoáy vào điểm vô lý" để họ tự nhận ra vấn đề, thay vì nhắc bài trực tiếp.

**5. Lát cắt:**

Học viên gõ lời giải thích khái niệm (vd: "vì sao LLM bịa") · AI phân tích và so khớp với tài liệu gốc để tìm chỗ hổng · AI đóng vai học trò hỏi ngược 1 câu ngây thơ xoáy đúng vào chỗ hổng đó · học viên nhận ra mâu thuẫn, tra cứu lại và diễn đạt lại kèm ví dụ đúng.

**6. AI tự làm đến đâu:**

* **Có điều kiện:** Tự đối chiếu (RAG) lời giải với nguồn chuẩn và tự sinh câu hỏi vặn ngược khi phát hiện lỗ hổng.
* **Tuyệt đối không làm:** Không mớm/cung cấp đáp án đúng, không phán xét đúng/sai trực tiếp.
* **Lý do:** Mớm đáp án sẽ triệt tiêu động lực tự suy nghĩ; phán xét như giám khảo làm mất an toàn tâm lý của môi trường luyện nháp.
* **Willing users:** Lê Minh Sang, Nguyễn Việt Hoàng, Nguyễn Tiến Phát.

**7. Phân công:**

* **Hồ Thái Hòa:** Product lead, canvas/spec, output contract, backend, RAG.
* **Nguyễn Đình Lâm Phúc:** Data & evidence, khảo sát, rubric, UI, luồng tương tác, user test.
* **Nguyễn Văn Hồng:** Golden set, system prompt, quality bar, eval, gọi model, validator.

**Vì sao đạt:**

Đi trúng pain point "ảo tưởng kiến thức" bằng chứng cứ số liệu thực tế cực sắc (65% user muốn bị AI hỏi vặn lại chứ không phải được nhắc bài). Định nghĩa rất rõ ranh giới "AI ngây thơ có kiểm soát" ở mục 6 để bảo vệ trải nghiệm sư phạm. Lát cắt mô tả gọn 1 chu kỳ học chủ động cốt lõi.