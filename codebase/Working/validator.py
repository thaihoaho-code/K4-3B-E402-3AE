import re
import json

def jaccard_similarity(s1: str, s2: str) -> float:
    # Hàm tính tỷ lệ trùng lặp từ vựng
    set1 = set(s1.lower().split())
    set2 = set(s2.lower().split())
    if not set1 or not set2:
        return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def check_copy_paste(user_text: str, topic_id: str) -> bool:
    try:
        with open("data/slide_corpus.json", "r", encoding="utf-8-sig") as f:
            corpus = json.load(f)
        for topic in corpus:
            if topic.get("topic_id") == topic_id or topic.get("id") == topic_id:
                for slide in topic.get("slides", []):
                    slide_text = slide.get("text", "")
                    # Nếu copy giống trên 60% thì chặn lại
                    if jaccard_similarity(user_text, slide_text) > 0.6:
                        return True
    except:
        pass
    return False

def is_out_of_scope(user_text: str) -> bool:
    # Chặn các từ khóa xin đáp án trực tiếp
    forbidden = ["đáp án", "giải", "chỉ cho", "làm hộ", "đúng không"]
    user_text_lower = user_text.lower()
    return any(word in user_text_lower for word in forbidden)
