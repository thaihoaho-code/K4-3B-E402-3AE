import json
import asyncio
from fastapi import APIRouter
from models import NoteRequest

router = APIRouter()
lock = asyncio.Lock()

@router.post("/notes")
async def save_note(req: NoteRequest):
    # TODO: Lưu reflection vào data/notes.json an toàn
    return {"saved": True}
