# -*- coding: utf-8 -*-
import os
import asyncio
from google import genai

client = genai.Client()

async def generate_content_stream(contents, config=None):
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = await client.aio.models.generate_content_stream(
                model=model_name,
                contents=contents, config=config
            )
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
            break
        except Exception as e:
            if attempt < max_retries - 1 and "503" in str(e):
                await asyncio.sleep(2 ** attempt)
            else:
                raise e
