import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models import ChatRequest
from llm import generate_content_stream
from retriever import retrieve
from validator import check_copy_paste, is_out_of_scope
from prompt import build_prompt, build_skip_prompt

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    async def sse_generator():
        try:
            # 1. Nếu người dùng bấm "Đổi góc hỏi" (Skip)
            if req.action == "skip":
                prompt = build_skip_prompt(len(req.asked_indexes) if req.asked_indexes else 0)
                async for text_chunk in generate_content_stream(prompt):
                    yield f"data: {json.dumps({'text': text_chunk})}\n\n"
                return

            # 2. Trạm kiểm soát (Validator): Chặn copy-paste và hỏi đáp án
            if check_copy_paste(req.user_text, req.topic_id):
                yield f"data: {json.dumps({'text': 'Dạ câu này giống hệt trong slide, anh/chị diễn đạt lại bằng ý hiểu của mình giúp em với ạ!'})}\n\n"
                return
                
            if is_out_of_scope(req.user_text):
                yield f"data: {json.dumps({'text': 'Dạ em là học trò nên không biết đáp án đâu ạ. Anh/chị gợi ý thêm cho em nhé!'})}\n\n"
                return

            # 3. RAG: Lục tìm slide liên quan nhất
            retrieved = retrieve(req.user_text, req.topic_id)
            
            # Fallback G10: Tạm thời hạ ngưỡng xuống 0.2 để test LLM
            if retrieved.confidence < 0.20:
                yield f"data: {json.dumps({'text': f'Dạ phần này em chưa rõ lắm, anh/chị có thể dùng khái niệm trong {retrieved.slide_ref} để giải thích cho em không ạ?', 'slide_ref': retrieved.slide_ref})}\n\n"
                return

            # 4. Ép vai học trò (Prompt) & Gọi LLM
            # Gộp prompt hệ thống và lời user lại
            system_prompt = build_prompt(retrieved.gap, retrieved.slide_ref, req.history)
            final_prompt = f"{system_prompt}\n\nNgười dùng nói: {req.user_text}" if system_prompt else req.user_text
            
            async for text_chunk in generate_content_stream(final_prompt):
                # Nhả chữ kèm theo slide_ref để hiển thị Nguồn
                yield f"data: {json.dumps({'text': text_chunk, 'slide_ref': retrieved.slide_ref})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'text': f'[Lỗi Backend]: {str(e)}'})}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")