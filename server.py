"""Web server for the AI Video Assistant.

Place next to main.py, with index.html inside a ./static folder.
    pip install fastapi uvicorn python-multipart
    uvicorn server:app --reload
Then open http://localhost:8000
"""
import os
import shutil
import tempfile
import uuid

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main import run_pipeline

app = FastAPI(title="AI Video Assistant")
SESSIONS: dict = {}  # session_id -> rag_chain (in memory; use Redis etc. in production)


def text(value) -> str:
    if isinstance(value, (list, tuple)):
        return "\n".join(f"- {v}" for v in value)
    return str(value or "")


@app.post("/api/process")
def process(
    source: str = Form(""),
    language: str = Form("english"),
    file: UploadFile | None = File(None),
):
    path = source.strip()
    if file and file.filename:
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
        path = tmp.name
    if not path:
        raise HTTPException(400, "Add a YouTube link or upload a file.")
    try:
        result = run_pipeline(path, language)
    except Exception as e:  # surface pipeline errors to the UI
        raise HTTPException(500, f"Processing failed: {e}")

    sid = uuid.uuid4().hex
    SESSIONS[sid] = result.pop("rag_chain")
    return {
        "session_id": sid,
        "title": text(result["title"]),
        "transcript": text(result["transcript"]),
        "summary": text(result["summary"]),
        "action_items": text(result["action_items"]),
        "key_decisions": text(result["key_decisions"]),
        "open_questions": text(result["open_questions"]),
    }


class ChatIn(BaseModel):
    session_id: str
    question: str


@app.post("/api/chat")
def chat(body: ChatIn):
    chain = SESSIONS.get(body.session_id)
    if not chain:
        raise HTTPException(404, "Session expired. Process the video again.")
    answer = chain.invoke(body.question)
    return {"answer": getattr(answer, "content", None) or text(answer)}


app.mount("/", StaticFiles(directory="static", html=True), name="static")