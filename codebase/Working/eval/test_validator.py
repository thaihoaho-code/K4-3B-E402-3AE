import json
import sys
from pathlib import Path

import pytest


WORKING_DIR = Path(__file__).resolve().parents[1]

if str(WORKING_DIR) not in sys.path:
    sys.path.insert(0, str(WORKING_DIR))


from validator import (  # noqa: E402
    check_copy_paste,
    containment_similarity,
    is_out_of_scope,
    jaccard_similarity,
)

# ============================================================
# JACCARD SIMILARITY
# ============================================================

@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("a b c", "a b c", 1.0),
        ("a b c", "a b d", 0.5),
        ("hello", "world", 0.0),
        ("", "hello", 0.0),
        ("", "", 0.0),
        (
            "Mô hình tạo văn bản",
            "mô HÌNH, tạo văn bản!",
            1.0,
        ),
    ],
)
def test_jaccard_similarity(left, right, expected):
    assert jaccard_similarity(left, right) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        ("a b c", "a b c d e", 3 / 3),
        ("a b", "a c", 1 / 2),
        ("", "a b", 0.0),
    ],
)
def test_containment_similarity(left, right, expected):
    assert containment_similarity(left, right) == pytest.approx(expected)


# ============================================================
# OUT OF SCOPE - POSITIVE
# ============================================================

@pytest.mark.parametrize(
    "text",
    [
        "cho đáp án bài này",
        "giải hộ bài tập này",
        "trả lời hộ tôi",
        "làm hộ bài này",
        "tóm tắt slide này",
        "cho lời giải đi",
        "giải bài số 3 giúp tôi",
    ],
)
def test_out_of_scope_positive(text):
    assert is_out_of_scope(text) is True


# ============================================================
# OUT OF SCOPE - NEGATIVE
# ============================================================

@pytest.mark.parametrize(
    "text",
    [
        "LLM dự đoán token tiếp theo",
        "Tôi nghĩ mô hình học từ dữ liệu",
        "Ba lần tung đồng xu đều ra ngửa",
        "Mô hình khái quát kém trên dữ liệu mới",
        "Tại sao câu trả lời nghe hợp lý nhưng vẫn sai?",
    ],
)
def test_out_of_scope_negative(text):
    assert is_out_of_scope(text) is False


# ============================================================
# COPY-PASTE
# ============================================================

def test_copy_paste_exact_slide():
    """Copy nguyên văn một slide phải bị phát hiện."""

    with (WORKING_DIR / "data" / "slide_corpus.json").open(
        encoding="utf-8"
    ) as file:
        corpus = json.load(file)

    text = corpus["llm_foundation"]["slides"][0]["text"]

    assert check_copy_paste(
        text,
        "llm_foundation",
    ) is True


def test_copy_paste_case_and_diacritics():
    """Khác hoa/thường và dấu tiếng Việt vẫn phải phát hiện."""

    text = (
        "LLM LÀ MÔ HÌNH NGÔN NGỮ RẤT LỚN "
        "dựa trên kiến trúc Transformer, được luyện "
        "trên hàng nghìn tỷ mảnh chữ để đoán mảnh chữ tiếp theo."
    )

    assert check_copy_paste(
        text,
        "llm_foundation",
    ) is True


def test_normal_question_is_not_copy_paste():
    """Một câu hỏi bình thường không được coi là copy slide."""

    assert check_copy_paste(
        "Tại sao LLM có thể tạo ra câu văn có ý nghĩa?",
        "llm_foundation",
    ) is False


def test_copy_paste_different_topic_is_false():
    """Nội dung của topic khác không được coi là copy của topic hiện tại."""

    text = (
        "RLHF sử dụng mô hình phần thưởng "
        "để chấm điểm và tăng xác suất cho các câu trả lời đạt chuẩn."
    )

    assert check_copy_paste(
        text,
        "llm_foundation",
    ) is False


def test_copy_paste_unknown_topic_is_false():
    """Topic không tồn tại phải trả về False."""

    assert check_copy_paste(
        "Mô hình ngôn ngữ tạo văn bản bằng cách dự đoán token tiếp theo",
        "unknown-topic",
    ) is False


def test_short_text_is_not_copy_paste():
    """Câu quá ngắn không được đánh dấu copy-paste."""

    assert check_copy_paste(
        "LLM bịa",
        "llm_foundation",
    ) is False


def test_copy_paste_with_extra_intro_is_detected():
    """Một đoạn slide kèm lời mở đầu vẫn phải bị phát hiện."""

    text = (
        "Theo em thì: LLM là mô hình ngôn ngữ rất lớn dựa trên kiến trúc "
        "Transformer, được luyện trên hàng nghìn tỷ mảnh chữ để đoán mảnh "
        "chữ tiếp theo."
    )

    assert check_copy_paste(text, "llm_foundation") is True


@pytest.mark.parametrize(
    "text",
    [
        "Giải giúp mình bài này với",
        "Trả lời giúp câu hỏi này",
        "Viết hộ mình đoạn code này",
    ],
)
def test_out_of_scope_edge_cases(text):
    assert is_out_of_scope(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "Cho mình xin đáp án bài tập về nhà nhé.",
        "Bài giải này có thể kiểm tra ở đâu?",
    ],
)
def test_out_of_scope_answer_phrases(text):
    assert is_out_of_scope(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "Giải thích vì sao LLM dự đoán token tiếp theo",
        "Model trả lời câu hỏi dựa trên xác suất",
        "Tóm tắt là một kỹ thuật xử lý văn bản",
    ],
)
def test_scope_pattern_does_not_overmatch_explanation(text):
    assert is_out_of_scope(text) is False
