"""FastAPI entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .db import get_connection, init_db
from .follow_up import FollowUpError, generate_follow_up
from .transcribe import transcribe

# Load local secrets (e.g. ANTHROPIC_API_KEY) from backend/.env, which is git-ignored.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="deep-dive-interview", lifespan=lifespan)


class Question(BaseModel):
    id: int
    category: str
    text: str


class Turn(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class FollowUpRequest(BaseModel):
    turns: list[Turn] = Field(min_length=1)


class FollowUpResponse(BaseModel):
    question: str


class TranscriptResponse(BaseModel):
    text: str


@app.get("/api/questions", response_model=list[Question])
def list_questions(category: str = "common") -> list[Question]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, category, text FROM questions WHERE category = ? ORDER BY id",
            (category,),
        ).fetchall()
    return [Question(**dict(row)) for row in rows]


@app.post("/api/follow-up", response_model=FollowUpResponse)
def follow_up(body: FollowUpRequest) -> FollowUpResponse:
    try:
        question = generate_follow_up([(t.question, t.answer) for t in body.turns])
    except FollowUpError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return FollowUpResponse(question=question)


@app.post("/api/transcribe", response_model=TranscriptResponse)
def transcribe_answer(file: UploadFile) -> TranscriptResponse:
    try:
        text = transcribe(file.file)
    except Exception as e:
        # Undecodable upload or a failed model download/load; report it to the UI.
        raise HTTPException(status_code=502, detail=f"Transcription failed: {e}") from e
    return TranscriptResponse(text=text)
