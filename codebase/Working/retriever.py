import json
import os
import numpy as np
from google import genai
from models import RetrieveResult

client = genai.Client()

def get_embedding(text: str) -> np.ndarray:
    """Gọi API tạo vector cho văn bản"""
    response = client.models.embed_content(
        model=os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"),
        contents=text,
    )
    return np.array(response.embeddings[0].values)

def load_or_build_cache():
    """Đọc dữ liệu, nếu chưa có vector thì gọi API tạo và lưu cache để đỡ tốn tiền gọi lại"""
    # Dùng utf-8-sig để tự động loại bỏ ký tự BOM nếu file được tạo từ Windows PowerShell
    with open("data/slide_corpus.json", "r", encoding="utf-8-sig") as f:
        raw_corpus = json.load(f)
    
    # Flatten the nested structure for RAG
    corpus = []
    for topic in raw_corpus:
        for slide in topic.get("slides", []):
            corpus.append({
                "topic_id": topic.get("topic_id") or topic.get("id"),
                "slide_id": slide.get("slide_ref"),
                "text": slide.get("text") or slide.get("content")
            })
            
    if not corpus:
        return [], []

    if os.path.exists("data/embeddings_cache.npy"):
        embeddings = np.load("data/embeddings_cache.npy")
    else:
        print("Build cache lần đầu...")
        embeddings = np.array([get_embedding(slide["text"]) for slide in corpus])
        np.save("data/embeddings_cache.npy", embeddings)
        
    return corpus, embeddings

def retrieve(user_text: str, topic_id: str) -> RetrieveResult:
    corpus, embeddings = load_or_build_cache()
    if not corpus:
        return RetrieveResult(gap="", slide_text="Chua co du lieu", slide_ref="Khong co", confidence=0.0)

    topic_indices = [i for i, c in enumerate(corpus) if c["topic_id"] == topic_id]
    if not topic_indices:
        return RetrieveResult(gap="", slide_text="Chua co du lieu", slide_ref="Khong co", confidence=0.0)

    user_emb = get_embedding(user_text)
    
    topic_embeddings = embeddings[topic_indices]
    norms = np.linalg.norm(topic_embeddings, axis=1) * np.linalg.norm(user_emb)
    similarities = np.dot(topic_embeddings, user_emb) / norms
    
    best_idx = np.argmax(similarities)
    best_slide = corpus[topic_indices[best_idx]]
    
    return RetrieveResult(
        gap="", slide_text=best_slide["text"],
        slide_ref=best_slide["slide_id"],
        confidence=float(similarities[best_idx])
    )