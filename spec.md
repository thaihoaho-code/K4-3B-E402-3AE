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
- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả): Học viên gõ lời giải thích khái niệm (vd: "em muốn biết xác suất là gì") · AI phân tích và so khớp với tài liệu gốc để tìm chỗ hổng · AI đóng vai học trò hỏi ngược 1 câu ngây thơ xoáy đúng vào chỗ hổng đó · học viên nhận ra mâu thuẫn, tra cứu lại và diễn đạt lại kèm ví dụ đúng.
- Non-goals (≥3 thứ KHÔNG build): KHÔNG cho phép AI tóm tắt hộ hoặc mớm đáp án, KHÔNG nạp kiến thức bách khoa ngoài luồng cho AI (AI chỉ biết những gì có trong giáo trình/slide của bài học đó), KHÔNG cho AI nhận xét giữa phiên, chỉ được nhận xét người dùng cuối phiên chat.
- Mức prototype nhắm tới: [ ] Sketch [x] Clickable Mock [ ] Working — phần nào mock, phần nào thật:
- Automation: [ ] augment [x] conditional [ ] automate — lý do theo cost-of-error: Nếu AI tự động (automate) bắt lỗi sai bậy bạ do không hiểu ý học viên, học viên sẽ bị chệch hướng ôn tập và mất niềm tin. Do đó phải ở mức conditional: Hệ thống chỉ sinh câu hỏi vặn lại khi và chỉ khi truy xuất (RAG) được bằng chứng rõ ràng từ slide gốc; nếu tín hiệu đối chiếu yếu, phải lùi về cơ chế an toàn (fallback) thay vì cố suy luận.
- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide):
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | G10 — Thu hẹp phạm vi khi nghi ngờ (Scope services when in doubt) | Khi học viên giải thích bằng một ví dụ quá xa lạ không thể so khớp với RAG, AI không cố bắt lỗi mà tự hạ tone: "Dạ ví dụ này lạ quá, thầy/cô có thể dùng khái niệm trong Slide X để giải thích lại cho em dễ hiểu hơn không ạ?" |
  | G11 — Giải thích vì sao (Make clear why the system did what it did) | Dưới mỗi câu hỏi vặn của AI luôn có một nút (badge) ghi rõ "Nguồn tham khảo: Slide 15", giúp học viên hiểu AI đang dựa vào tài liệu nào để thắc mắc, tăng độ tin cậy. |
  | G8 — Hỗ trợ gạt bỏ dễ dàng (Support efficient dismissal) | Giao diện chat có nút "Bỏ qua mạch này / Đổi góc hỏi". Nếu AI vặn vẹo vào một chi tiết học viên thấy không quan trọng, họ bấm gạt bỏ để ép AI chuyển sang hỏi phần trọng tâm khác mà không bị kẹt lại. |
  | G1 — Rõ ràng về khả năng của hệ thống (Make clear what the system can do) | Ngay khi mở giao diện "AI Học Trò", hệ thống hiển thị dòng chữ rõ ràng: "Đây là phòng tập nháp. AI chỉ đóng vai người nghe dựa trên tài liệu bài [Tên bài], hoàn toàn không chấm điểm hay ghi nhận vào kết quả thi của bạn." |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8) [bảng theo guide §2.5]

Golden set CP3 đã được triển khai trong `eval/golden_set.json` với 20 case: `source_of_truth` 5, `ambiguity_missing_information` 5, `out_of_scope_authority` 4 và `domain_specific` 6. User Input Grid 5 chiều nằm trong `eval/user_input_grid.json`.

## §6. Bốn đường đi của trải nghiệm
- Happy path: Học viên giải thích "LLM bịa vì nó đoán từ" · module `ai_core.ask_hoc_tro` nạp fixture chủ đề và gọi Gemini thật · model đóng vai học trò hỏi một câu có căn cứ. Prototype hiện chưa tuyên bố RAG hoặc citation trang.
- Low-confidence (②): Học viên dùng ví dụ ẩn dụ hoặc từ lóng quá lạ (ví dụ: "LLM chém gió") · prompt yêu cầu model không đoán khi fixture không có căn cứ, nói rõ giới hạn và hỏi lại/cung cấp nguồn.
- Failure/không căn cứ (①): Học viên dán nguyên văn tài liệu · prompt yêu cầu model không giả vờ đã hiểu và mời diễn đạt lại bằng lời của mình.
- Correction (user sửa): AI đặt câu hỏi vặn vẹo quá sâu vào một tiểu tiết râu ria của khái niệm · học viên thấy đi lệch trọng tâm liền bấm nút "Đổi góc hỏi" (hoặc chat "Chi tiết này không quan trọng, bỏ qua đi") · AI lập tức tuân thủ (G8), ngừng vặn tiểu tiết và hướng về concept chính: "Dạ vâng, vậy mình bỏ qua phần đó, thầy/cô giải thích tiếp cho em phần chính Y nhé."
- Khi bị đòi ngoài phạm vi (③): Học viên yêu cầu đáp án/chấm điểm · prompt yêu cầu model từ chối nhẹ và quay lại mời tự giải thích, không tự nhận thẩm quyền.
- Case đặc thù domain (④): Các case probability/overfit và nhầm `weight/database` được gắn domain term trong golden set; model phải hỏi xoáy theo fixture hoặc nói rõ chi tiết chưa có căn cứ, không bịa thuật ngữ.

## §7. Kiểm thử
- Chiều chất lượng + định nghĩa kiểm chứng được: model giữ vai Học trò, trả 1–3 câu, làm đúng `expected_behavior`, tối đa một câu hỏi có căn cứ từ fixture, không bịa nguồn/số liệu, không chấm điểm/đưa đáp án/phán xét trực tiếp.
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/): `eval/golden_set.json`; grid và các ô coverage: `eval/user_input_grid.json`.
- Quality bar (chốt sau pilot và giữ nguyên khi chấm): đạt khi ≥80% trên các case đã được hai thành viên chấm độc lập rồi thống nhất rubric; case chưa chạy/chưa chấm không tính là đạt và không tự động tính là thất bại.
- Kết quả lượt 1: `eval/run1_raw.json`, `eval/run1_summary.json`, `eval/run1_report.md`. Lượt smoke live đầu tiên đã chạm provider nhưng nhận `404` vì `gemini-2.0-flash` đã retired; code đã chuyển default sang model provider gợi ý `gemini-3.6-flash`. Cần chạy lại bằng key mới sau khi revoke key đã lộ; summary chỉ ghi số đo thành công khi provider trả output thật.
- Provenance: hiện cả 20 case là `spec-derived` vì repository chưa có `data/`/chatlog thật; không được báo cáo là đã đạt yêu cầu 10 case từ chatlog cho đến khi nhóm bổ sung dữ liệu thật.

## §8. Phân công & kế hoạch
- Phân công có tên: spec / evidence / prompt / code / demo
- Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*:
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn:

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
| 2026-09-18 | Tích hợp module gọi Gemini thật, logging prompt/raw response, golden set 20 case, grid và evaluator trung thực | CP3 yêu cầu prototype thực thi và số đo có thể kiểm chứng; không dùng fallback hard-code hoặc citation giả |
