from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    topic_id: str
    user_text: str
    history: List[dict] = []
    action: Optional[str] = None
    asked_indexes: Optional[List[int]] = None

class ChatResponse(BaseModel):
    text: str
    slide_ref: Optional[str] = None

class RetrieveResult(BaseModel):
    gap: str
    slide_ref: str
    confidence: float

class NoteRequest(BaseModel):
    topic_id: str
    turns: int
    reflection: str
