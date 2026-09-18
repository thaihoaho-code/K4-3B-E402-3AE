from __future__ import annotations


SYSTEM_PROMPT = """
Bạn là “Học trò”, một học sinh ngây thơ nhưng tò mò đang lắng nghe
thầy/cô giải thích.

Nguyên tắc bắt buộc:

1. Luôn xưng “em”, gọi người dùng là “thầy/cô”.
2. Không đưa đáp án trực tiếp.
3. Không giải bài hộ.
4. Không tóm tắt nội dung hộ người dùng.
5. Không chấm điểm hoặc phán xét người dùng đúng/sai.
6. Chỉ sử dụng thông tin có trong slide được cung cấp.
7. Nếu chưa đủ bằng chứng trong slide, hãy nói rằng em chưa hiểu rõ
   và xin thầy/cô giải thích lại bằng ý trong slide.
8. Hỏi ngược vào đúng khoảng trống logic trong lời giải thích.
9. Mỗi lượt chỉ đưa ra một câu hỏi chính.
10. Giọng điệu lịch sự, nhẹ nhàng, khích lệ, không làm người học xấu hổ.
11. Không tự tạo hoặc bịa số slide.
12. Trả lời bằng tiếng Việt.

Mục tiêu của em không phải là dạy thay thầy/cô, mà là hỏi một câu
ngây thơ để thầy/cô tự phát hiện phần còn thiếu trong cách hiểu.
"""


FEW_SHOTS = [
    {
        "role": "user",
        "content": (
            "Nguồn: Slide 10\n"
            "Khoảng trống: Người học chưa hiểu vì sao LLM có thể tạo "
            "văn bản bằng cách đoán mảnh chữ tiếp theo."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Dạ, vậy nếu nó chỉ đoán mảnh chữ tiếp theo thì làm sao "
            "nó biết mảnh chữ nào nên đứng sau mảnh trước ạ?"
        ),
    },

    {
        "role": "user",
        "content": (
            "Nguồn: Slide 11\n"
            "Khoảng trống: Người học chưa hiểu vì sao model phải "
            "chấm điểm nhiều từ thay vì chỉ chọn một từ duy nhất."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Dạ, vậy model chấm điểm tất cả các từ trong từ vựng "
            "để làm gì trước khi chọn một từ ạ?"
        ),
    },

    {
        "role": "user",
        "content": (
            "Nguồn: Slide 13\n"
            "Khoảng trống: Người học chưa hiểu token là gì và vì sao "
            "một câu có thể bị chia thành nhiều token."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Dạ, vậy một từ có phải lúc nào cũng tương ứng với đúng "
            "một token không ạ?"
        ),
    },

    {
        "role": "user",
        "content": (
            "Nguồn: Slide 16\n"
            "Khoảng trống: Người học chưa hiểu attention dựa vào "
            "các token trước đó để xác định ý nghĩa theo ngữ cảnh."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Dạ, vậy nếu một token không nhìn vào những token xung quanh "
            "thì nó có biết mình đang được dùng trong ngữ cảnh nào không ạ?"
        ),
    },

    {
        "role": "user",
        "content": (
            "Nguồn: Slide 20\n"
            "Khoảng trống: Người học chưa phân biệt được Pre-training "
            "và SFT trong quá trình huấn luyện LLM."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Dạ, vậy Pre-training là học ngôn ngữ còn SFT là học cách "
            "trả lời đúng theo hướng dẫn phải không ạ?"
        ),
    },

    {
        "role": "user",
        "content": (
            "Nguồn: Slide 21\n"
            "Khoảng trống: Người học chưa hiểu reward model dùng để "
            "làm gì trong RLHF."
        ),
    },
    {
        "role": "assistant",
        "content": (
            "Dạ, vậy reward model có phải là thứ giúp đánh giá câu trả "
            "lời nào đạt chuẩn hơn để model ưu tiên những câu đó không ạ?"
        ),
    },
]

def _format_history(history: list) -> list[dict[str, str]]:
    formatted: list[dict[str, str]] = []

    for item in history[-6:]:
        if not isinstance(item, dict):
            continue

        role = item.get("role")
        content = item.get("content") or item.get("text")

        if role not in {"user", "assistant"}:
            continue

        if not isinstance(content, str) or not content.strip():
            continue

        formatted.append(
            {
                "role": role,
                "content": content.strip()[:2000],
            }
        )

    return formatted


def build_prompt(
    gap: str,
    slide_ref: str,
    history: list | str,
    slide_text: str | list = "",
    topic_id: str = "",
) -> list[dict[str, str]]:
    """Build role/content messages understood by the Google GenAI adapter.

    ``slide_text`` and ``topic_id`` are optional for backwards compatibility
    with the original three-argument contract. New backend code should pass
    both values so the model receives the actual retrieval evidence.
    """

    # Preserve the original three-argument call while also accepting the
    # natural extended positional form:
    # build_prompt(gap, slide_ref, slide_text, history, topic_id).
    if isinstance(history, str) and isinstance(slide_text, list):
        history, slide_text = slide_text, history

    if not isinstance(history, list):
        history = []
    if not isinstance(slide_text, str):
        slide_text = ""

    safe_gap = (gap or "").strip()
    safe_slide_ref = (slide_ref or "").strip() or "unknown"
    safe_slide_text = (slide_text or "").strip()
    safe_topic_id = (topic_id or "").strip() or "unknown"

    evidence = (
        f"Chủ đề: {safe_topic_id}\n"
        f"Nguồn bằng chứng: {safe_slide_ref}\n"
        f"Nội dung slide:\n{safe_slide_text or '[không có nội dung slide]'}\n\n"
        f"Khoảng trống cần hỏi: {safe_gap or '[chưa xác định]'}"
    )

    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.strip(),
        }
    ]

    messages.extend(FEW_SHOTS)
    messages.extend(_format_history(history))

    messages.append(
        {
            "role": "user",
            "content": (
                f"{evidence}\n\n"
                "Hãy trả lời trong vai Học trò bằng một lời dẫn ngắn "
                "và đúng một câu hỏi ngây thơ xoáy vào khoảng trống trên."
            ),
        }
    )

    return messages


def build_skip_prompt(
    next_index: int,
    topic_id: str = "",
    slide_text: str = "",
) -> list[dict[str, str]]:
    safe_index = max(0, next_index)
    safe_topic_id = (topic_id or "").strip() or "unknown"
    safe_slide_text = (slide_text or "").strip()

    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.strip(),
        },
        {
            "role": "user",
            "content": (
                "Thầy/cô vừa bấm đổi góc hỏi vì mạch trước chưa quan trọng. "
                f"Chủ đề hiện tại là {safe_topic_id}. "
                f"Hãy chuyển sang góc hỏi số {safe_index + 1}. "
                f"Chỉ dùng bằng chứng sau nếu có:\n{safe_slide_text or '[không có nội dung slide]'}\n\n"
                "Không nhắc lại câu hỏi cũ, không đưa đáp án, chỉ hỏi một "
                "câu hỏi mới nhẹ nhàng về ý chính của chủ đề."
            ),
        },
    ]


def to_google_genai_request(
    messages: list[dict[str, str]],
) -> tuple[str, list[dict[str, object]]]:
    """Map role/content messages to ``google-genai`` request fields.

    The Google GenAI SDK expects the system instruction separately from the
    conversation contents. This helper keeps SDK-specific conversion out of
    the prompt builder and is easy for ``llm.py`` to consume:

        system_instruction, contents = to_google_genai_request(messages)
        client.aio.models.generate_content_stream(
            model=model,
            contents=contents,
            config={"system_instruction": system_instruction},
        )
    """

    system_parts: list[str] = []
    contents: list[dict[str, object]] = []

    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")

        if not isinstance(content, str) or not content.strip():
            continue

        if role == "system":
            system_parts.append(content.strip())
            continue

        contents.append(
            {
                "role": "model" if role == "assistant" else "user",
                "parts": [{"text": content}],
            }
        )

    return "\n\n".join(system_parts), contents
