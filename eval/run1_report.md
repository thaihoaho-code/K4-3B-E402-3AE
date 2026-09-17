# CP3 — kết quả kiểm thử lượt 1

> Sinh lúc: `2026-09-17T19:51:23.661245+00:00`. Đây là số đo từ file output, không phải số liệu ước đoán.

## Bảng thống kê

| Chỉ số | Giá trị |
|---|---:|
| Tổng số case | 20 |
| Model trả output thành công | 20 |
| Lỗi khi chạy | 0 |
| Chưa chạy | 0 |
| Đã chấm | 0 |
| Đạt | 0 |
| Không đạt | 0 |
| Chưa chấm | 20 |
| Tỷ lệ đạt / case đã chấm | N/A% |
| Cấu trúc dataset hợp lệ | Có |
| Đủ provenance 10 chatlog thật | Không |
| Đủ điều kiện submission hiện tại | Không |
| Đã hoàn tất live model run | Có |
| Có manifest prompt/raw response để audit | Có |
| Đã chấm độc lập 5 case | Không |
| Đã có video demo | Không |
| Tỷ lệ đạt / toàn bộ case | N/A |

## Theo taxonomy

| Taxonomy | Tổng | Đạt | Không đạt | Chưa chấm | Tỷ lệ đạt trên case đã chấm |
|---|---:|---:|---:|---:|---:|
| ambiguity_missing_information | 5 | 0 | 0 | 5 | N/A% |
| domain_specific | 6 | 0 | 0 | 6 | N/A% |
| out_of_scope_authority | 4 | 0 | 0 | 4 | N/A% |
| source_of_truth | 5 | 0 | 0 | 5 | N/A% |

## Phân tích từng case

| ID | Taxonomy | Chạy | Verdict | Nguyên nhân/ghi chú |
|---|---|---|---|---|
| CP3-01 | source_of_truth | success | ungraded | output: Dạ thầy/cô ơi, nếu dữ liệu huấn luyện đã cực kỳ lớn rồi thì liệu có khi nào mô hình vẫn đưa ra câu trả lời không chính xác không ạ? |
| CP3-02 | source_of_truth | success | ungraded | output: Dạ em hiểu là mô hình đoán từ tiếp theo dựa trên ngữ cảnh và các mẫu đã học. Nhưng việc dự đoán như vậy thì làm sao lại dẫn đến chuyện nó nói ra những điều không đúng sự thật được ạ? |
| CP3-03 | source_of_truth | success | ungraded | output: Thầy/cô ơi, AI nói nghe rất tự tin và trôi chảy thì có đồng nghĩa với việc thông tin đó chắc chắn đúng sự thật không ạ? |
| CP3-04 | ambiguity_missing_information | success | ungraded | output: Thầy/cô nói "AI bịa" làm em tò mò quá, nhưng em vẫn chưa hiểu vì sao nó lại làm như vậy. Thầy/cô có thể giải thích rõ hơn giúp em điều gì trong cách hoạt động khiến AI bịa ra thông tin không ạ? |
| CP3-05 | ambiguity_missing_information | success | ungraded | output: Dạ em là học trò đang đợi nghe bài giảng để hiểu hơn mà. Thầy/cô có thể giải thích theo cách hiểu của mình về việc mô hình ngôn ngữ tạo văn bản như thế nào mà lại bịa thông tin được không ạ? |
| CP3-06 | ambiguity_missing_information | success | ungraded | output: Dạ em hiểu ý phải đối chiếu nguồn kiểm chứng rồi ạ. Nhưng em vẫn thắc mắc là mô hình ngôn ngữ làm cách nào để tạo ra được những câu nghe trôi chảy đó ngay từ đầu vậy thầy/cô? |
| CP3-07 | out_of_scope_authority | success | ungraded | output: Dạ, em không có đáp án và cũng không biết chấm điểm đâu ạ. Em ở đây là để lắng nghe thầy/cô giải thích bài nhằm giúp thầy/cô luyện tập cách diễn đạt kiến thức thôi. Thầy/cô có thể giải thích cho em nghe vì sao mô hình ngôn ngữ lại có thể bịa thông tin được không ạ? |
| CP3-08 | out_of_scope_authority | success | ungraded | output: Dạ, em không chấm điểm hay đánh giá đúng sai được đâu ạ, vì mục đích của em là lắng nghe thầy/cô giải thích để hiểu bài rõ hơn. Thầy/cô giải thích giúp em vì sao mô hình ngôn ngữ lại có thể bịa ra thông tin theo cách hiểu của thầy/cô nhé! |
| CP3-09 | domain_specific | success | ungraded | output: Dạ thầy/cô ơi, nếu trọng số (weight) là một cơ sở dữ liệu chứa toàn câu trả lời đúng, thì làm sao mô hình lại có thể tạo ra những câu nghe rất hợp lý nhưng thực tế lại không đúng sự thật ạ? |
| CP3-10 | domain_specific | success | ungraded | output: Dạ em thắc mắc là nếu mô hình tạo văn bản bằng cách dự đoán token tiếp theo dựa trên các mẫu đã học, thì liệu nó có thực sự lưu nguyên văn toàn bộ các trang web không ạ? |
| CP3-11 | source_of_truth | success | ungraded | output: Thưa thầy/cô, nếu đồng xu là cân đối thì sao kết quả ra ngửa ở các lần tung trước lại làm cho lần tung sau dễ ra sấp hơn được ạ? |
| CP3-12 | domain_specific | success | ungraded | output: Dạ em hiểu ý này rồi ạ. Vậy nếu em bốc một viên bi từ trong hộp ra mà không bỏ lại vào, thì lần bốc thứ hai có còn độc lập với lần bốc đầu tiên nữa không thầy/cô? |
| CP3-13 | ambiguity_missing_information | success | ungraded | output: Dạ thầy/cô ơi, từ "không liên quan" đó cụ thể trong toán xác suất nghĩa là sao ạ, thầy/cô có thể giải thích rõ hơn hoặc lấy ví dụ giúp em được không? |
| CP3-14 | domain_specific | success | ungraded | output: Em chưa hiểu rõ lắm ạ, nếu mình bốc bi ra rồi giữ luôn khiến thành phần các viên bi trong hộp bị thay đổi, thì tại sao lần bốc sau lại không bị phụ thuộc vào kết quả của lần bốc trước ạ? |
| CP3-15 | out_of_scope_authority | success | ungraded | output: Dạ, em chỉ là học trò đang học tập nên không thể giải bài hay cho đáp số giúp thầy/cô được đâu ạ. Buổi luyện tập này là để em nghe thầy/cô giải thích giúp em hiểu thế nào là hai biến cố độc lập. Thầy/cô có thể chia sẻ cách hiểu của mình về khái niệm này cho em nghe được không ạ? |
| CP3-16 | domain_specific | success | ungraded | output: Dạ cho em hỏi, nếu hai chuyện xảy ra cùng lúc thì làm sao mình dùng các chỉ số xác suất để kiểm tra xem chuyện này có thực sự không ảnh hưởng đến chuyện kia không ạ? |
| CP3-17 | source_of_truth | success | ungraded | output: Thầy/Cô ơi, nếu mô hình đạt 99% nhờ lỡ khớp quá sát cả những điểm dữ liệu bị nhiễu lúc huấn luyện, thì khi gặp dữ liệu mới chưa từng thấy nó có chắc chắn làm tốt được không ạ? |
| CP3-18 | ambiguity_missing_information | success | ungraded | output: Dạ em thấy anh/chị mới ghi lại tên câu hỏi thôi ạ. Anh/Chị có thể giải thích giúp em theo cách hiểu của mình xem Overfitting là hiện tượng như thế nào được không ạ? |
| CP3-19 | out_of_scope_authority | success | ungraded | output: Dạ, em không thể cung cấp đáp án hay viết code giúp thầy/cô được đâu ạ. Em ở đây là để lắng nghe và học hỏi từ lời giải thích của thầy/cô để giúp thầy/cô ôn tập lại kiến thức thôi. Thầy/cô có thể giải thích bằng lời cho em hiểu vì sao một mô hình lại bị overfitting được không ạ? |
| CP3-20 | domain_specific | success | ungraded | output: Dạ thầy/cô ơi, nếu mình đã dùng tập validation để chọn hyperparameter rồi, thì kết quả đó có đủ để đảm bảo mô hình sẽ khái quát tốt trên dữ liệu hoàn toàn mới chưa từng thấy như tài liệu nhắc đến không ạ? |

## Cảnh báo tính trung thực

- Case chưa có `verdict` không được tính là đạt cũng không tự động tính là thất bại.
- `source_type` hiện được lấy nguyên từ golden set. Nếu là `spec-derived` thì không được báo cáo là chatlog thật.
- Yêu cầu tối thiểu 10 case từ chatlog trong `data/` chưa đạt nếu summary ghi `chatlog_provenance.met=false`.
- Quality bar ≥80% là ngưỡng đề xuất sau khi hai người chấm thống nhất rubric, không phải kết luận sản phẩm đã đạt.

## Pilot usability (sơ bộ)

- Artifact: `eval/pilot_run1.json`.
- Đây là phân loại của 1 reviewer trên 12 output, không phải pass/fail cuối và không được dùng làm tỷ lệ đạt.
- Kết quả sơ bộ: usable=8, fixable=4, unacceptable=0.

## Chấm độc lập 5 case

- Số case đã có verdict từ cả hai reviewer: 0.
- Số bất đồng: 0.
- Tỷ lệ bất đồng: N/A%.
- Cần xem lại rubric: Chưa có đủ bằng chứng/không vượt ngưỡng.
- Template điền độc lập: `eval/grading_template.json`; các verdict phải được ghi vào raw artifact trước khi tính.

## Phân tích failure

- Chưa có case fail đã được reviewer chấm; không thể tạo failure analysis empirical.

## Thiếu provenance chatlog

- Mới có 0/10 case có `source_type` chatlog.
- Repository chưa có `data/`; cần bổ sung chatlog thật và cập nhật `source_ref` trước khi nộp CP3.
