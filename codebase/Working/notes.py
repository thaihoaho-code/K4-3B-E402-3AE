import json
import asyncio
import os
from fastapi import APIRouter
from models import NoteRequest

router = APIRouter()
lock = asyncio.Lock() # Tránh trường hợp 2 người cùng ghi file 1 lúc

@router.post("/notes")
async def save_note(req: NoteRequest):
    filepath = "data/notes.json"
    
    async with lock:
        # Đọc file cũ lên
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    notes = json.load(f)
                except:
                    notes = []
        else:
            notes = []
            
        # Nối data mới vào và lưu lại
        notes.append(req.model_dump())
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
            
    return {"saved": True, "message": "Đã lưu log thành công"}