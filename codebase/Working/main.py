from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import chat
import notes

app = FastAPI(title="Agent Hoc Tro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(notes.router)

# Phục vụ file HTML/JS/CSS cho frontend (mount cuối cùng)
app.mount("/", StaticFiles(directory=".", html=True), name="static")
