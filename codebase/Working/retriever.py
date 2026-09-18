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
    """So sánh câu hỏi với vector slide, trả về slide liên quan nhất"""
    corpus, embeddings = load_or_build_cache()
    if not corpus:
        return RetrieveResult(gap="Chưa có dữ liệu", slide_ref="Không có", confidence=0.0)

    # 1. Biến câu hỏi thành vector
    user_emb = get_embedding(user_text)
    
    # 2. Tính độ tương đồng Cosine (Cosine Similarity)
    norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(user_emb)
    similarities = np.dot(embeddings, user_emb) / norms
    
    # 3. Lấy slide có điểm cao nhất
    best_idx = np.argmax(similarities)
    best_slide = corpus[best_idx]
    
    return RetrieveResult(
        gap=best_slide["text"],
        slide_ref=best_slide["slide_id"],
        confidence=float(similarities[best_idx])
    )