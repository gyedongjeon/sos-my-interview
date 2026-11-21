"""Saved interview attempts: answers, scores, feedback, and recordings."""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .db import DB_PATH, get_connection
from .evaluate import Feedback, SpeakingFeedback

RECORDINGS_DIR = DB_PATH.parent / "recordings"

router = APIRouter(prefix="/api")


class AttemptCreate(BaseModel):
    question_id: int


class AttemptSummary(BaseModel):
    id: int
    question_id: int
    question: str
    # Title of the job posting the question belongs to; None for common questions.
    posting_title: str | None
    created_at: str  # ISO 8601, UTC
    english_score: int | None
    content_score: int | None


class SavedTurn(BaseModel):
    position: int
    question: str
    answer: str
    clarity: int | None
    unclear_words: list[str]
    words_per_minute: int | None
    recording_url: str | None
    has_video: bool


class AttemptDetail(AttemptSummary):
    turns: list[SavedTurn]
    feedback: Feedback | None
    speaking: SpeakingFeedback | None


class FeedbackSave(BaseModel):
    feedback: Feedback
    speaking: SpeakingFeedback | None = None
    english_score: int = Field(ge=0, le=100)
    content_score: int = Field(ge=0, le=100)


SUMMARY_SQL = """
    SELECT a.id, a.question_id, q.text AS question, p.title AS posting_title, a.created_at,
           a.english_score, a.content_score, a.feedback, a.speaking
    FROM attempts a
    JOIN questions q ON q.id = a.question_id
    LEFT JOIN job_postings p ON p.id = q.posting_id
"""


def _require_attempt(conn, attempt_id: int):
    row = conn.execute(SUMMARY_SQL + " WHERE a.id = ?", (attempt_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Attempt not found.")
    return row


def _save_recording(attempt_id: int, position: int, source: BinaryIO) -> str:
    folder = RECORDINGS_DIR / str(attempt_id)
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{position}.webm"
    with open(folder / name, "wb") as target:
        shutil.copyfileobj(source, target)
    return name


@router.post("/attempts", response_model=AttemptSummary)
def create_attempt(body: AttemptCreate) -> AttemptSummary:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_connection() as conn:
        if conn.execute("SELECT 1 FROM questions WHERE id = ?", (body.question_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Question not found.")
        cursor = conn.execute(
            "INSERT INTO attempts (question_id, created_at) VALUES (?, ?)",
            (body.question_id, created_at),
        )
        row = _require_attempt(conn, cursor.lastrowid)
    return AttemptSummary(**{k: row[k] for k in AttemptSummary.model_fields})


@router.get("/attempts", response_model=list[AttemptSummary])
def list_attempts() -> list[AttemptSummary]:
    """All attempts that have at least one answer, newest first."""
    with get_connection() as conn:
        rows = conn.execute(
            SUMMARY_SQL
            + " WHERE EXISTS (SELECT 1 FROM attempt_turns t WHERE t.attempt_id = a.id)"
            + " ORDER BY a.created_at DESC, a.id DESC"
        ).fetchall()
    return [AttemptSummary(**{k: row[k] for k in AttemptSummary.model_fields}) for row in rows]


@router.get("/attempts/{attempt_id}", response_model=AttemptDetail)
def get_attempt(attempt_id: int) -> AttemptDetail:
    with get_connection() as conn:
        row = _require_attempt(conn, attempt_id)
        turns = conn.execute(
            "SELECT * FROM attempt_turns WHERE attempt_id = ? ORDER BY position", (attempt_id,)
        ).fetchall()
    return AttemptDetail(
        **{k: row[k] for k in AttemptSummary.model_fields},
        turns=[
            SavedTurn(
                position=t["position"],
                question=t["question"],
                answer=t["answer"],
                clarity=t["clarity"],
                unclear_words=json.loads(t["unclear_words"]),
                words_per_minute=t["words_per_minute"],
                recording_url=(
                    f"/api/attempts/{attempt_id}/recordings/{t['position']}" if t["recording"] else None
                ),
                has_video=bool(t["has_video"]),
            )
            for t in turns
        ],
        feedback=json.loads(row["feedback"]) if row["feedback"] else None,
        speaking=json.loads(row["speaking"]) if row["speaking"] else None,
    )


@router.post("/attempts/{attempt_id}/turns", status_code=201)
def add_turn(
    attempt_id: int,
    question: str = Form(),
    answer: str = Form(""),
    clarity: int | None = Form(None),
    unclear_words: str = Form("[]"),
    words_per_minute: int | None = Form(None),
    has_video: bool = Form(False),
    recording: UploadFile | None = None,
) -> dict[str, int]:
    """Append one answered question (and its recording) to an attempt."""
    try:
        words = json.loads(unclear_words)
        if not isinstance(words, list):
            raise ValueError
    except ValueError as e:
        raise HTTPException(status_code=422, detail="unclear_words must be a JSON list.") from e

    with get_connection() as conn:
        _require_attempt(conn, attempt_id)
        position = conn.execute(
            "SELECT COALESCE(MAX(position), 0) + 1 FROM attempt_turns WHERE attempt_id = ?",
            (attempt_id,),
        ).fetchone()[0]
        name = _save_recording(attempt_id, position, recording.file) if recording else None
        conn.execute(
            """
            INSERT INTO attempt_turns
                (attempt_id, position, question, answer, clarity, unclear_words,
                 words_per_minute, recording, has_video)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (attempt_id, position, question, answer, clarity, json.dumps(words),
             words_per_minute, name, int(has_video)),
        )
    return {"position": position}


@router.put("/attempts/{attempt_id}/feedback", status_code=204)
def save_feedback(attempt_id: int, body: FeedbackSave) -> None:
    with get_connection() as conn:
        _require_attempt(conn, attempt_id)
        conn.execute(
            "UPDATE attempts SET feedback = ?, speaking = ?, english_score = ?, content_score = ? WHERE id = ?",
            (
                body.feedback.model_dump_json(),
                body.speaking.model_dump_json() if body.speaking else None,
                body.english_score,
                body.content_score,
                attempt_id,
            ),
        )


@router.delete("/attempts/{attempt_id}", status_code=204)
def delete_attempt(attempt_id: int) -> None:
    with get_connection() as conn:
        _require_attempt(conn, attempt_id)
        conn.execute("DELETE FROM attempts WHERE id = ?", (attempt_id,))
    shutil.rmtree(RECORDINGS_DIR / str(attempt_id), ignore_errors=True)


@router.get("/attempts/{attempt_id}/recordings/{position}")
def get_recording(attempt_id: int, position: int) -> FileResponse:
    path: Path = RECORDINGS_DIR / str(attempt_id) / f"{position}.webm"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Recording not found.")
    return FileResponse(path, media_type="video/webm")
