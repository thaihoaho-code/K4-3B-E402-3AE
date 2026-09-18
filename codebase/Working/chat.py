from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models import ChatRequest

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # TODO: Gọi validator -> retriever -> prompt -> llm stream
    pass
