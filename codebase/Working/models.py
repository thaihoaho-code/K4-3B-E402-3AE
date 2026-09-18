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
    # Nội dung slide cần được truyền sang prompt để model chỉ lập luận
    # trên bằng chứng mà retriever đã chọn. Đặt ở cuối để giữ tương thích
    # với cách khởi tạo cũ: RetrieveResult(gap, slide_ref, confidence).
    slide_text: str = ""


class NoteRequest(BaseModel):
    topic_id: str = Field(min_length=1)
    turns: int = Field(ge=0)
    reflection: str = Field(min_length=1)
