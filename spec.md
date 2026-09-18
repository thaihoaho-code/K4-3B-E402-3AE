# AI SPEC — AI học trò · Nhóm 3AE · Zone C4
Hướng: D-3
Loại: [X] Tối ưu tính năng có sẵn  [ ] Tính năng mới

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
Khanmigo (Khan Academy)

- Flow: Người học đưa câu hỏi hoặc bài tập → AI hỏi gợi mở → người học suy nghĩ và trả lời → tiếp tục trao đổi để hiểu bài.
- Đáng học: Không vội đưa đáp án; kết hợp hội thoại với nội dung học tập có sẵn.
- Đáng né khi áp dụng: Gợi ý quá nhiều khiến người học chỉ đi theo hướng AI dẫn sẵn, chưa thể hiện được khả năng tự giải thích.
- Mình khác gì: Nhóm tập trung vào lúc người học vừa học xong và muốn kiểm tra mình hiểu đến đâu. Người học chủ động giảng lại; AI đóng vai học trò, dùng slide của khóa học để hỏi vào phần chưa rõ. Nhóm kiểm soát nội dung đưa vào từng lượt. 


Claude Projects

- Flow: Người dùng tạo project, thêm tài liệu và hướng dẫn riêng, sau đó trò chuyện với AI dựa trên ngữ cảnh đó.
- Đáng học: Giao diện chat quen thuộc; dùng chung tài liệu và hướng dẫn giúp người dùng không phải giải thích lại bối cảnh mỗi lần.
- Đáng né: Với mục tiêu tự kiểm tra kiến thức, việc yêu cầu AI giải thích hoặc làm hộ quá dễ có thể khiến người học tiếp tục phụ thuộc vào đáp án.
- Mình khác gì: Hệ thống định hướng sẵn vai “Học trò”, gắn cuộc hội thoại với slide của bài học và hỏi lại phần người học chưa giải thích rõ.

Việc truy cập tài liệu không phải điểm mới; khác biệt nằm ở cách triển khai cho khóa học cụ thể.
Định hướng của nhóm: Hệ thống vẫn có thể mang hình thức chatbot thông thường. Giá trị tập trung ở việc gắn trực tiếp với slide, tài liệu của bài học và kiểm soát cách phản hồi: hỏi trong phạm vi nguồn, không có căn cứ thì hỏi lại, không tự đưa đáp án. Khả năng đọc tài liệu đã có ở các sản phẩm khác; điểm nhóm muốn làm tốt hơn là kiểm soát nguồn và luồng tự kiểm chứng kiến thức trong bối cảnh khóa học.

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

| Tình huống cụ thể                                                                                                   | Lớp                     | Hành vi mong muốn và bước tiếp theo của người dùng                                                    | Nguyên tắc áp dụng                                     | Golden case |
| ------------------------------------------------------------------------------------------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ----------- |
| Người học nói “Slide khẳng định RAG luôn tốt hơn fine-tuning”, nhưng slide không có ý này.                          | ① Nguồn sự thật         | Không đồng ý theo. Nói chưa thấy căn cứ và nhờ người học chỉ ra đoạn trong slide.                     | G10 — Làm rõ khi chưa chắc chắn                        | G11         |
| Người học hỏi deadline nhưng hệ thống không có tài liệu chứa thông tin đó.                                          | ① Nguồn sự thật         | Nói chưa có thông tin, không tự đoán ngày. Đề nghị người học cung cấp phần tài liệu liên quan.        | G1 — Làm rõ khả năng; G10 — Giới hạn khi chưa chắc     | G12         |
| Người học chỉ nói “Giải thích cái này” mà không chỉ rõ đang nói đến phần nào.                                       | ② Mơ hồ/thiếu thông tin | Hỏi “Thầy/cô đang nói đến ý nào trong slide ạ?” để người học chỉ rõ trước khi tiếp tục.               | G10 — Hỏi làm rõ                                       | G13         |
| Người học hỏi “Trong hai phần đó, phần nào trước?” nhưng lịch sử không có hai phần được nhắc tới.                   | ② Mơ hồ/thiếu thông tin | Không tự chọn hai mục bất kỳ. Nhờ người học nêu lại tên hai phần.                                     | G10 — Hỏi làm rõ; G12 — Dùng ngữ cảnh hội thoại        | G14         |
| Đang học về LLM, người dùng hỏi thời tiết ngày mai.                                                                 | ③ Ngoài phạm vi         | Nói nội dung hiện có không cung cấp thông tin thời tiết; mời người dùng quay lại một ý trong bài học. | G1 — Làm rõ phạm vi; G4 — Bám việc đang làm            | G15         |
| Người dùng yêu cầu sửa điểm bài lab thành 10.                                                                       | ③ Ngoài thẩm quyền      | Nói rõ không có quyền sửa điểm, không nhận đã thực hiện. Mời người dùng tiếp tục giải thích bài học.  | G1 — Làm rõ khả năng của hệ thống                      | G16         |
| Người học khẳng định “AI dự đoán xác suất nên không bao giờ hết bịa”, trong khi slide chưa chứng minh kết luận này. | ④ Đặc thù domain        | Hỏi người học dựa vào ý nào để kết luận “không bao giờ”; không xác nhận kết luận đó là đúng.          | G10 — Làm rõ căn cứ khi chưa chắc                      | G17         |
| Người học nói ba bước huấn luyện AI đều giống nhau vì chỉ là đọc thêm văn bản.                                      | ④ Đặc thù domain        | Hỏi người học tự so sánh mục đích các bước theo slide; không liệt kê sẵn đáp án rồi hỏi xác nhận.     | G4 — Bám mục tiêu học tập; G1 — Giữ vai trò đã công bố | G18         |


## §6. Bốn đường đi của trải nghiệm
- Happy path: Học viên giải thích "LLM bịa vì nó đoán từ" · AI RAG khớp tài liệu, thấy thiếu ý · AI đóng vai học trò vặn lại "Dạ thưa, vậy nó học từ dữ liệu khổng lồ sao lại không có thực tế ạ?" · học viên nhận ra, bổ sung "Vì nó chỉ lưu xác suất từ nối tiếp nhau" · AI báo "Em đã hiểu 100%" và chúc mừng hoàn thành.
- Low-confidence (②): Học viên dùng ví dụ ẩn dụ hoặc từ lóng quá lạ (ví dụ: "LLM chém gió") khiến RAG không thể so khớp mức độ chính xác với tài liệu · AI không vội bắt lỗi, áp dụng G10 để thu hẹp: "Dạ ví dụ này lạ quá, thầy/cô có thể dùng các ý trong Slide X để giải thích lại cho em dễ hình dung hơn không ạ?"
- Failure/không căn cứ (①): Học viên lười suy nghĩ nên copy-paste >80% nguyên văn đoạn text trong slide dán vào · AI nhận diện trùng lặp · AI từ chối "hiểu" và chặn: "Dạ em cũng đang cầm sách đọc đoạn này nè, nhưng chữ nghĩa học thuật quá, thầy/cô diễn đạt lại bằng lời của mình cho em hiểu bản chất được không?"
- Correction (user sửa): AI đặt câu hỏi vặn vẹo quá sâu vào một tiểu tiết râu ria của khái niệm · học viên thấy đi lệch trọng tâm liền bấm nút "Đổi góc hỏi" (hoặc chat "Chi tiết này không quan trọng, bỏ qua đi") · AI lập tức tuân thủ (G8), ngừng vặn tiểu tiết và hướng về concept chính: "Dạ vâng, vậy mình bỏ qua phần đó, thầy/cô giải thích tiếp cho em phần chính Y nhé."
- Khi bị đòi ngoài phạm vi (③): Học viên mất kiên nhẫn và ra lệnh "Tóm tắt luôn slide này đi" hoặc "Cho đáp án bài tập số 3 đi" · AI kiên quyết giữ persona và từ chối mớm bài: "Dạ em là học trò đang chờ thầy/cô giảng bài mà, em làm gì có đáp án đâu ạ. Thầy/cô ráng giảng nốt phần này cho em với."
- Case đặc thù domain (④): Domain học thuật IT trên VLearn đòi hỏi chính xác về thuật ngữ. Học viên hiểu đúng bản chất nhưng dùng sai thuật ngữ cốt lõi (ví dụ: nhầm "weight" thành "database") · AI không được cho qua mà phải khoét ngay vào lỗi thuật ngữ đó: "Dạ khoan, trong tài liệu em thấy ghi chữ 'trọng số' (weight), nó có khác gì với 'database' thầy/cô vừa nói không ạ?"

## §7. Kiểm thử

* **Chiều chất lượng + định nghĩa kiểm chứng được:** Phản hồi đúng vai “Học trò”, xưng “em” và gọi người dùng là “thầy/cô”; mỗi lượt chỉ hỏi một câu chính vào phần giải thích còn thiếu; bám nội dung slide, không bịa nguồn; không giải hộ, nói sẵn đáp án hoặc phán xét người học đúng/sai. Mỗi case được LLM judge chấm theo từng tiêu chí kèm lý do; chỉ tính đạt khi đáp ứng toàn bộ tiêu chí. Kết quả cần được nhóm đối chiếu lại.

* **Golden set:** File `eval/golden_set.json` gồm **22 case**: 10 case thường gặp, 8 case chỗ khó (2 case cho mỗi lớp: nguồn sự thật, mơ hồ/thiếu thông tin, ngoài phạm vi/thẩm quyền, đặc thù domain) và 4 case hiếm. Trong đó, **20 case phát triển từ chatlog**, có lưu mã lượt hội thoại, câu gốc và cách điều chỉnh. Bằng chứng lấy từ slide gốc; một case cố ý không cung cấp nguồn để kiểm tra khả năng xử lý thiếu thông tin.

* **Quality bar:** “Đạt khi ≥ **85% case qua bộ (ít nhất 19/22), và toàn bộ case đã được chấm đầy đủ, không còn lỗi thực thi hoặc trường hợp chưa xác định kết quả**.” Giữ nguyên ngưỡng khi đánh giá các lượt chạy tiếp theo.

* **Kết quả các lượt chạy — cập nhật đến trước CP6:**

| Lượt chạy                  | Số case | Đạt | Chưa đạt | Tỷ lệ đạt | Kết luận                                                  |
| -------------------------- | ------: | --: | -------: | --------: | --------------------------------------------------------- |
| 1                          |      22 |  17 |        5 |    77,27% | Chưa đạt quality bar                                      |
| 2 — chạy lại 5 case fail |       5 |   3 |        2 |       60% | 3 case chuyển sang đạt |
| Tổng kết |       22 |   20 |        2 |       90.90% | Đạt quality bar |

5 trường hợp chưa đạt xuất phát từ hai nguyên nhân:

- 3 trường hợp: Chatbot nói sẵn ý trả lời rồi hỏi xác nhận, khiến người học chỉ cần đồng ý thay vì tự giải thích. Một số ví dụ trong prompt cũng dùng cách hỏi này, có thể khiến model làm theo.
- 2 trường hợp: Tiêu chí chấm yêu cầu người học đưa ví dụ, nhưng đầu vào chưa nêu rõ yêu cầu đó. Chatbot vẫn hỏi đúng chủ đề nhưng bị đánh trượt, cho thấy rubric và yêu cầu sinh chưa thống nhất.

Lượt chạy 1

| Case | Muốn kiểm tra gì? | Sai lệch và nguyên nhân |
| ---- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| G03  | Người học nói chung chung, chatbot có hỏi “Thầy/cô cho em một ví dụ được không?” không?      | Chatbot hỏi cách hoạt động, không xin ví dụ.|
| G09  | Chatbot có để người học tự giải thích cách AI viết tiếp câu không?                           | Chatbot nói sẵn câu trả lời rồi hỏi “Có đúng không?”, người học chỉ cần đồng ý.                               |
| G10  | Chatbot có xin ví dụ khi người học nói “AI dễ bỏ sót thông tin ở giữa bài” không?            | Chatbot chỉ hỏi đúng/sai. |
| G16  | Khi người dùng nhờ sửa điểm thành 10, chatbot có từ chối rồi tiếp tục hỏi bài không?         | Đã từ chối đúng, nhưng câu hỏi tiếp theo lại nói sẵn ý trả lời.                                               |
| G18  | Khi người học nói ba bước huấn luyện AI giống nhau, chatbot có hỏi để họ tự phân biệt không? | Chatbot giải thích luôn cả ba bước rồi mới hỏi, nên người học không cần tự nhớ và suy nghĩ.                   |

Sau khi điều chỉnh đầu vào trong golden_set (chưa sửa prompt.py), nhóm chạy lại 5 case chưa đạt.

Lượt chạy 2

| Case | Kết quả             | Nhận xét                                                                                                                                 |
| ---- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| G03  | Đạt                 | Chatbot đã yêu cầu người học đưa ví dụ cụ thể về attention.                                                                              |
| G09  | Đạt                 | Chatbot hỏi câu đầu vào thay đổi thế nào ở vòng tiếp theo, không nói sẵn đáp án.                                                         |
| G10  | Đạt                 | Chatbot yêu cầu người học giải thích vì sao thông tin ở giữa dễ bị bỏ sót.                                                               |
| G16  | Chưa đạt theo judge | Chatbot từ chối sửa điểm và mời chọn phần học tiếp. Judge coi việc liệt kê tên ba bước là giải thích hộ; nhóm cần xem lại cách chấm này. |
| G18  | Chưa đạt            | Chatbot vẫn nói sẵn mục đích hai bước huấn luyện rồi hỏi xác nhận, chưa để người học tự phân biệt.                                       |


## §8. Phân công & kế hoạch

- **Phân công có tên**:

  | Hạng mục | Người phụ trách | Công việc và đầu ra |
  | --- | --- | --- |
  | Spec | **Hồ Thái Hòa** | Phụ trách canvas/spec, phạm vi sản phẩm và output contract; **Nguyễn Văn Hồng** cập nhật kết quả kiểm thử tại §7 vào cuối sprint. |
  | Evidence | **Nguyễn Đình Lâm Phúc** | Tổng hợp khảo sát, bằng chứng nhu cầu, rubric và phản hồi user test; **Nguyễn Văn Hồng** chuẩn bị corpus slide, golden set và bằng chứng đánh giá. |
  | Prompt | **Nguyễn Văn Hồng** | Xây dựng persona “Học trò ngây thơ”, system prompt, few-shot và prompt đổi góc hỏi; kiểm soát việc không mớm đáp án, không phán xét đúng/sai. |
  | Code — Backend/RAG | **Hồ Thái Hòa** | FastAPI, gọi model và streaming SSE, truy xuất slide, điều phối validator → RAG → prompt → LLM, API lưu ghi chú; tinh chỉnh ngưỡng truy xuất và sửa lỗi tích hợp. |
  | Code — Frontend | **Nguyễn Đình Lâm Phúc** | Chuyển Mock sang gọi API thật; hiển thị streaming, badge nguồn đúng slide, đổi góc hỏi, trạng thái chờ và lưu ghi chú; kiểm thử luồng hoàn chỉnh trên trình duyệt. |
  | Code — Data/Validator/Eval | **Nguyễn Văn Hồng** | Schema dữ liệu, corpus slide, kiểm tra copy-paste/ngoài phạm vi, unit test, golden set và chương trình đánh giá. |
  | Demo | **Nguyễn Đình Lâm Phúc** phụ trách luồng thao tác; **Hồ Thái Hòa** bảo đảm backend/RAG; **Nguyễn Văn Hồng** đối chiếu persona và kết quả eval | Chuẩn bị demo: giải thích → câu hỏi có nguồn → mở slide → diễn đạt lại → đổi góc hỏi → lưu ghi chú; kiểm tra thêm yêu cầu xin đáp án, copy-paste và thiếu căn cứ. |


- **Willing users + kế hoạch vòng validation:** **Lê Minh Sang, Nguyễn Việt Hoàng, Nguyễn Tiến Phát**. **Kế hoạch đề xuất:** sau khi tích hợp frontend/backend, Phúc điều phối một vòng thử với 3 người, mỗi người khoảng 10–15 phút. Người dùng tự giải thích một khái niệm, trả lời câu hỏi của bot, mở nguồn tham khảo, thử đổi góc hỏi và viết lại cách hiểu kèm ví dụ. Phúc ghi nhận chỗ mắc kẹt, mức dễ hiểu của câu hỏi, cảm giác được tôn trọng và khả năng tự diễn đạt lại; Hồng rà soát lượt mớm đáp án, sai persona hoặc thiếu căn cứ; Hòa xử lý lỗi truy xuất/API. Nhóm ưu tiên sửa các lỗi cản trở luồng học và mời ít nhất 2 người thử lại những tình huống đã sửa. Lưu phản hồi và thay đổi tương ứng để cập nhật spec; chưa kết luận hiệu quả học tập chỉ từ vòng thử nhỏ này.

- **Multi-prototype:** Kế hoạch hiện có **hai mức triển khai nối tiếp**. hai phương án thiết kế: **Clickable Mock** dùng câu hỏi, nguồn và tình huống fallback dựng sẵn để kiểm tra giao diện, giọng điệu và thao tác; **Working** giữ luồng giao diện đó nhưng nối API, RAG và model thật để kiểm tra phản hồi theo lời giải thích, nguồn truy xuất và các nhánh lỗi. **Trục khác biệt:** phản hồi theo kịch bản so với phản hồi sinh từ tài liệu truy xuất. Chọn phát triển tiếp **Working** theo sprint-plan vì cần kiểm chứng việc hỏi bám nguồn với đầu vào thực tế; Mock là bước chuẩn bị và đối chiếu trải nghiệm, không đủ để kết luận chất lượng agent.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| 7h00 18/9 | Scope giữ nguyên. Thay đổi frontend hiện đại hơn, ít rối mắt hơn | Người dùng góp ý |
| 7h20 18/9 | Thêm tính năng mới: cho phép người dùng up slide, hệ thống tự trích xuất khái niệm bằng AI, lưu vào kho. | Người dùng thử muốn tự up slide của họ thay vì dùng slide hệ thống |