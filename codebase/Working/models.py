from typing import Any, Literal
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    topic_id: str = Field(min_length=1)
    user_text: str = ""
    history: list[dict[str, Any]] = Field(default_factory=list)
    action: Literal["skip"] | None = None
    asked_indexes: list[int] = Field(default_factory=list)

class ChatResponse(BaseModel):
    text: str
    slide_ref: str | None = None

class RetrieveResult(BaseModel):
    gap: str
    slide_ref: str
    confidence: float = Field(ge=0.0, le=1.0)
    slide_text: str = ""

class NoteRequest(BaseModel):
    topic_id: str = Field(min_length=1)
    turns: int = Field(ge=0)
    reflection: str = Field(min_length=1)

class IngestSlide(BaseModel):
    slide_ref: str
    text: str

class IngestRequest(BaseModel):
    title: str
    slides: list[IngestSlide]
