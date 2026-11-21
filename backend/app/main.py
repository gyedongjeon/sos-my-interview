"""FastAPI entry point."""

from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException, Response, UploadFile
from pydantic import BaseModel, Field

from .attempts import router as attempts_router
from .background import router as background_router
from .db import get_connection, init_db
from .evaluate import Feedback, SpeakingFeedback, evaluate, evaluate_speaking
from .follow_up import generate_follow_up
from .llm import LLMError
from .speech import synthesize
from .transcribe import to_wav, transcribe

# Load local secrets (e.g. GEMINI_API_KEY) from backend/.env, which is git-ignored.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="deep-dive-interview", lifespan=lifespan)
app.include_router(attempts_router)
app.include_router(background_router)


class Question(BaseModel):
    id: int
    category: str
    text: str
    # The job posting a tailored question was written for; None for common questions.
    posting_id: int | None


class Turn(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class FollowUpRequest(BaseModel):
    turns: list[Turn] = Field(min_length=1)
    # The saved question being answered; selects the job posting used as context.
    question_id: int | None = None


class FollowUpResponse(BaseModel):
    question: str


class TranscriptResponse(BaseModel):
    text: str
    clarity: int | None
    unclear_words: list[str]
    words_per_minute: int | None


class SpeechRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class EvaluateRequest(BaseModel):
    turns: list[Turn] = Field(min_length=1)
    question_id: int | None = None


@app.get("/api/questions", response_model=list[Question])
def list_questions() -> list[Question]:
    """Common questions plus the tailored questions of every job posting."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, category, text, posting_id FROM questions"
            " WHERE category != 'archived' ORDER BY id"
        ).fetchall()
    return [Question(**dict(row)) for row in rows]


@app.post("/api/follow-up", response_model=FollowUpResponse)
def follow_up(body: FollowUpRequest) -> FollowUpResponse:
    try:
        question = generate_follow_up([(t.question, t.answer) for t in body.turns], body.question_id)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return FollowUpResponse(question=question)


@app.post("/api/transcribe", response_model=TranscriptResponse)
def transcribe_answer(file: UploadFile) -> TranscriptResponse:
    try:
        result = transcribe(file.file)
    except Exception as e:
        # Undecodable upload or a failed model download/load; report it to the UI.
        raise HTTPException(status_code=502, detail=f"Transcription failed: {e}") from e
    return TranscriptResponse(**asdict(result))


@app.post("/api/evaluate", response_model=Feedback)
def evaluate_answers(body: EvaluateRequest) -> Feedback:
    try:
        return evaluate([(t.question, t.answer) for t in body.turns], body.question_id)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@app.post("/api/evaluate/speaking", response_model=SpeakingFeedback)
def evaluate_speaking_answers(
    files: list[UploadFile],
    questions: list[str] = Form(),
    transcripts: list[str] = Form(),
) -> SpeakingFeedback:
    """Score how the answers sound. Each file pairs with the question/transcript at its index."""
    if not (len(files) == len(questions) == len(transcripts)):
        raise HTTPException(status_code=422, detail="files, questions, and transcripts must align.")
    try:
        clips = [
            (question, transcript, to_wav(file.file))
            for file, question, transcript in zip(files, questions, transcripts)
        ]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Could not read the audio: {e}") from e
    try:
        return evaluate_speaking(clips)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@app.post("/api/speech")
def speech(body: SpeechRequest) -> Response:
    try:
        audio = synthesize(body.text)
    except Exception as e:
        # Failed model download/load or synthesis; the UI falls back to the browser voice.
        raise HTTPException(status_code=502, detail=f"Speech synthesis failed: {e}") from e
    return Response(content=audio, media_type="audio/wav")

