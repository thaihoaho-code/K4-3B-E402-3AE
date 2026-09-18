import json
import os
import re
from fastapi import APIRouter
from models import IngestRequest
from llm import generate_content

router = APIRouter()

CORPUS_FILE = "data/slide_corpus.json"
CACHE_FILE = "data/embeddings_cache.npy"

def clean_title(title: str) -> str:
    topic_id = title.replace(".pdf", "").strip()
    topic_id = re.sub(r'[^a-zA-Z0-9_]', '_', topic_id).lower()
    return topic_id

@router.post("/ingest")
async def ingest_slides(req: IngestRequest):
    cleaned_slides = []
    
    system_instruction = (
        "Bạn là biên tập viên. Nhiệm vụ: xóa nhiễu từ văn bản thô của slide (link, câu hỏi, icon, tên trường, số trang). "
        "Chỉ giữ lại định nghĩa cốt lõi, kiến thức chính. Trình bày ngắn gọn, rõ ràng thành 1 đoạn văn. "
        "Tuyệt đối không bịa thêm thông tin."
    )
    
    for slide in req.slides:
        prompt = "Lọc nhiễu và rút gọn nội dung sau:\n" + slide.text
        
        try:
            cleaned_text = await generate_content(
                prompt,
                config={'system_instruction': system_instruction}
            )
        except Exception as e:
            cleaned_text = slide.text # fallback
            
        cleaned_slides.append({
            "slide_ref": slide.slide_ref,
            "text": cleaned_text.strip()
        })
        
    topic_id = clean_title(req.title)
    
    corpus = []
    if os.path.exists(CORPUS_FILE):
        with open(CORPUS_FILE, "r", encoding="utf-8") as f:
            try:
                corpus = json.load(f)
            except:
                pass
                
    found = False
    for topic in corpus:
        if topic.get("topic_id") == topic_id:
            topic["slides"].extend(cleaned_slides)
            found = True
            break
            
    if not found:
        corpus.append({
            "title": req.title,
            "slides": cleaned_slides,
            "topic_id": topic_id
        })
        
    with open(CORPUS_FILE, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
        
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        
    return {
        "message": "Success",
        "topic": {
            "title": req.title,
            "topic_id": topic_id,
            "slides": cleaned_slides
        }
    }
