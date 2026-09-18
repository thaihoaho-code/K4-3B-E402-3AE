from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import chat
import notes
import ingest

app = FastAPI(title="Agent Hoc Tro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(notes.router)
app.include_router(ingest.router)

app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/", StaticFiles(directory="Frontend", html=True), name="static")
