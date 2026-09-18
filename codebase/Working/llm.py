import os
from google import genai

client = genai.Client()

async def generate_content_stream(contents, config=None):
    """Gọi Gemini sinh chữ dạng stream (bất đồng bộ)"""
    
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    
    response = await client.aio.models.generate_content_stream(
        model=model_name,
        contents=contents, config=config
    )
    
    async for chunk in response:
        if chunk.text:
            yield chunk.text