from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path


COPY_PASTE_THRESHOLD = 0.8
MIN_COPY_TOKENS = 8
MIN_CONTAINMENT_TOKENS = 8

CORPUS_PATH = Path(__file__).resolve().parent / "data" / "slide_corpus.json"


def _normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = text.casefold().replace("đ", "d")

    text = unicodedata.normalize("NFD", text)
    text = "".join(
        character
        for character in text
        if unicodedata.category(character) != "Mn"
    )

    return text


def _tokens(text: str) -> set[str]:
    normalized = _normalize_text(text)
    return set(re.findall(r"\b[\w]+\b", normalized, flags=re.UNICODE))


def jaccard_similarity(s1: str, s2: str) -> float:
    tokens_1 = _tokens(s1)
    tokens_2 = _tokens(s2)

    # Không coi hai chuỗi rỗng là copy-paste.
    if not tokens_1 or not tokens_2:
        return 0.0

    intersection = tokens_1 & tokens_2
    union = tokens_1 | tokens_2

    return len(intersection) / len(union)


def containment_similarity(s1: str, s2: str) -> float:
    """Return the fraction of the smaller token set contained in the other.

    Jaccard penalizes a pasted slide when the learner adds a short prefix or
    suffix. Containment catches that case while the minimum-token guard in
    ``check_copy_paste`` prevents short, generic questions from being flagged.
    """

    tokens_1 = _tokens(s1)
    tokens_2 = _tokens(s2)

    if not tokens_1 or not tokens_2:
        return 0.0

    return len(tokens_1 & tokens_2) / min(len(tokens_1), len(tokens_2))


def _load_corpus() -> dict:
    if not CORPUS_PATH.exists():
        return {}

    with CORPUS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def check_copy_paste(user_text: str, topic_id: str) -> bool:
    user_tokens = _tokens(user_text)

    # Tránh đánh dấu nhầm các câu rất ngắn.
    if len(user_tokens) < MIN_COPY_TOKENS:
        return False

    corpus = _load_corpus()
    topic = corpus.get(topic_id)

    if not topic:
        return False

    for slide in topic.get("slides", []):
        slide_text = slide.get("text", "")
        slide_tokens = _tokens(slide_text)
        if len(slide_tokens) < MIN_CONTAINMENT_TOKENS:
            continue

        similarity = jaccard_similarity(user_text, slide_text)
        containment = containment_similarity(user_text, slide_text)

        if (
            similarity >= COPY_PASTE_THRESHOLD
            or (
                containment >= COPY_PASTE_THRESHOLD
                and len(user_tokens) >= MIN_CONTAINMENT_TOKENS
            )
        ):
            return True

    return False


_SCOPE_PATTERN = re.compile(
    r"(?:"
    r"\bdap\s+an\b|"
    r"\bbai\s+giai\b|"
    r"\bcho\s+(?:dap\s+an|loi\s+giai)\b|"
    r"\b(?:giai|tra\s+loi|lam|viet)\s+(?:ho|giup)\b|"
    r"\b(?:giai|lam)\s+bai\b|"
    r"\btom\s+tat\b(?!\s+la\b)"
    r")"
)


def is_out_of_scope(user_text: str) -> bool:
    normalized = _normalize_text(user_text)
    return bool(_SCOPE_PATTERN.search(normalized))
