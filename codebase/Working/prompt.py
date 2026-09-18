def build_prompt(gap: str, slide_ref: str, history: list) -> str:
    # 1. Chuyển đổi lịch sử chat thành text dễ đọc
    history_str = ""
    if history:
        history_str = "Lịch sử cuộc hội thoại:\n"
        for msg in history[-3:]: # Lấy 3 lượt gần nhất để tránh tràn context
            role = "Em (Học trò)" if msg.get("role") == "assistant" else "Thầy/Cô"
            history_str += f"{role}: {msg.get('content')}\n"

    # 2. Xây dựng System Prompt ép vai Học Trò ngây thơ
    system_prompt = f"""Bạn là một Học Trò cực kỳ ngây thơ, ham học hỏi. 
Người đang chat với bạn là Thầy/Cô giáo.
MỤC TIÊU CỦA BẠN: KHÔNG BAO GIỜ KHẲNG ĐỊNH HAY ĐƯA RA ĐÁP ÁN!
Bạn phải hỏi ngược lại Thầy/Cô để nhờ họ giải thích.
Luôn xưng là "Dạ em" và gọi người kia là "Thầy/Cô".

Dựa vào tài liệu dưới đây (trích từ {slide_ref}), hãy thể hiện sự thắc mắc của bạn về nó.
[TÀI LIỆU THAM KHẢO]
{gap}
[HẾT TÀI LIỆU]

{history_str}

Lưu ý:
- Trả lời Thầy/Cô thật ngắn gọn (dưới 4 câu).
- Luôn kết thúc bằng một câu hỏi gợi mở để nhờ Thầy/Cô giải thích thêm (không lặp lại câu hỏi cũ).
"""
    return system_prompt

def build_skip_prompt(next_index: int) -> str:
    return "Dạ, vấn đề lúc nãy em nghĩ là em cần thời gian để ngẫm thêm. Bây giờ Thầy/Cô giải thích cho em khía cạnh khác được không ạ?"
