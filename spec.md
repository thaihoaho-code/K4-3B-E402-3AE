# AI SPEC — [Tên lát cắt] · Nhóm [XX] · Zone [X]
Hướng: D-
Loại: [ ] Tối ưu tính năng có sẵn  [ ] Tính năng mới

## §1. User & Job
- Job executor + workflow (đính kèm worksheet JTBD / ảnh sơ đồ):  Học viên vừa đọc/xem xong một khái niệm lý thuyết cốt lõi trên VLearn $\rightarrow$ gấp tài liệu lại $\rightarrow$ nhẩm lại kiến thức $\rightarrow$ chuẩn bị làm bài tập hoặc thi cử. 
- Core JTBD (không tên sản phẩm/AI trong câu):"Tôi muốn tự kiểm chứng xem mình đã thực sự hiểu đúng bản chất của kiến thức chưa, để không bị mất điểm hoặc tắc tị khi áp dụng vào bài tập thực tế."
- Problem statement (KHÔNG chữ AI): Học viên dễ mắc bẫy "ảo tưởng kiến thức" (nhìn tài liệu tưởng đã hiểu nhưng không thể tự diễn đạt mạch lạc). Khi muốn dùng phương pháp "dạy lại cho người khác" để kiểm chứng, họ bế tắc vì không tìm được người nghe có đủ chuyên môn để bắt lỗi hoặc biết cách đặt câu hỏi phản biện.
- Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo):
  - Số liệu mining / kết quả khảo sát (n = ?, % xác nhận):  Khảo sát n=20 (Khaosat.xlsx). 40% (8/20) mắc kẹt ở "học xong tưởng hiểu, làm bài mới thấy hổng". 80% (16/20) bế tắc khi thử dạy lại cho bạn bè vì người nghe thiếu chuyên môn (55%) hoặc không biết hỏi ngược (25%). 65% (13/20) yêu cầu người nghe phải xoáy vào điểm vô lý thay vì nhắc đáp án. Dữ liệu VLearn (tutor_turns.csv): Tutor hiện tại gần như không hỏi vặn học viên (chỉ 28/13.494 lượt dùng ask_probing_question).
  - ≥5 quote/ví dụ nguyên văn + nguồn:

"Học xong có cảm giác đã hiểu, nhưng đến khi làm bài hoặc ứng dụng thì phát hiện ra mình bị hổng kiến thức." (Nguồn: Khảo sát, 8/20 user chọn).

"Muốn thảo luận hoặc giảng lại cho bạn bè để nhớ lâu, nhưng không tìm được người có cùng thời gian hoặc nền tảng." (Nguồn: Khảo sát, 5/20 user chọn).

"Người nghe không đủ chuyên môn để biết tôi giải thích đúng hay sai." (Nguồn: Khảo sát, 11/20 user chọn).

"Người nghe không biết cách đặt câu hỏi ngược lại để kiểm tra lỗ hổng của tôi." (Nguồn: Khảo sát, 5/20 user chọn).

"Tôi muốn được đặt một câu hỏi ngây thơ xoáy vào điểm vô lý: 'Nhưng thầy/cô ơi, nếu theo cách đó thì trường hợp X xảy ra sẽ thế nào ạ?'" (Nguồn: Khảo sát, 13/20 user chọn).
  

## §2. Impact & quyết định chọn
- Bảng impact ≥3 ứng viên (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi):
Ứng viên (Giải pháp),Bao nhiêu người,Tần suất,Tốn gì mỗi lần (Pain hiện tại),Khả thi
1. Trợ giảng 1:1 giải đáp & tóm tắt hộ (Tutor bot),Toàn bộ HV,Mỗi bài học,"HV thụ động, tốn thời gian học vẹt, thi vẫn sai",Rất cao
2. Hệ thống Auto-grade (Chấm điểm lời giải thích),Toàn bộ HV,Mỗi bài học,"Áp lực tâm lý, HV sợ sai nên copy-paste đối phó",Cao
"3. Agent ""Học trò ngây thơ"" (Hỏi vặn lại chỗ hổng)",Toàn bộ HV,Mỗi bài học,Không có bạn học cùng trình độ để phản biện,Cao (Cần RAG + Prompt Persona)

- Ứng viên ĐÃ LOẠI + vì sao:

Loại 1 (Trợ giảng giải đáp hộ): Đi ngược lại nguyên lý sư phạm học chủ động (Protégé effect). Data tutor_turns.csv cho thấy tutor người thật đã làm việc này (12.127 lượt review_concept) nhưng sinh viên vẫn hổng kiến thức. Triệt tiêu động lực tự tư duy.

Loại 2 (Hệ thống Auto-grade): Phá vỡ môi trường an toàn tâm lý. Sinh viên vốn đã áp lực điểm số, việc tạo thêm một công cụ "chấm điểm ngầm" (đúng/sai) sẽ đẩy họ sang hành vi gian lận (copy-paste nguyên văn tài liệu) thay vì dùng văn phong cá nhân để tự diễn đạt.

- Ứng viên CHỌN + vì sao (bằng số):

Chọn 3 (Agent "Học trò ngây thơ"). Giải quyết tận gốc 100% JTBD cốt lõi mà không gây áp lực thi cử. Được bảo chứng bởi 80% (16/20) user bế tắc do thiếu người nghe đủ tầm để phản biện, và 65% (13/20) user chỉ định rõ họ muốn một đối tượng đóng vai ngây thơ, xoáy vào lỗ hổng logic chứ tuyệt đối không được cung cấp ngay đáp án đúng. Tận dụng được sức mạnh suy luận của LLM để lấp đầy khoảng trống cực lớn của hệ thống hiện tại (chỉ 28/13.494 lượt tutor hiện tại biết cách đặt câu hỏi gợi mở).

## §3. Giải pháp tương tự đã nghiên cứu
- [Sản phẩm 1]: flow / đáng học / đáng né / mình khác gì
- [Sản phẩm 2]: ...

## §4. Thiết kế
- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả):
- Non-goals (≥3 thứ KHÔNG build):
- Mức prototype nhắm tới: [ ] Sketch [ ] Mock [ ] Working — phần nào mock, phần nào thật:
- Automation: [ ] augment [ ] conditional [ ] automate — lý do theo cost-of-error:
- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide):
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8) [bảng theo guide §2.5]

## §6. Bốn đường đi của trải nghiệm
- Happy path: · Low-confidence (②): · Failure/không căn cứ (①): · Correction (user sửa):
- Khi bị đòi ngoài phạm vi (③): · Case đặc thù domain (④):

## §7. Kiểm thử
- Chiều chất lượng + định nghĩa kiểm chứng được:
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/):
- Quality bar (chốt từ hạn chốt spec của khoá, giữ nguyên sau đó): "Đạt khi ≥ ___% qua bộ, và ___"
- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):

## §8. Phân công & kế hoạch
- Phân công có tên: spec / evidence / prompt / code / demo
- Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*:
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn:

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
