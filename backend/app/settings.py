"""User preferences stored in the database (single user, so one global set)."""

import os

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .db import get_connection

router = APIRouter(prefix="/api")


class Settings(BaseModel):
    # Language the written feedback is in, as an English name (e.g. "Korean").
    # None until the user (or the browser's language, on first visit) has chosen one.
    feedback_language: str | None = Field(default=None, min_length=1, max_length=40)


def _get(key: str) -> str | None:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def feedback_language() -> str:
    """The language to write feedback in: the saved choice, else FEEDBACK_LANGUAGE, else English."""
    return _get("feedback_language") or os.environ.get("FEEDBACK_LANGUAGE", "").strip() or "English"


@router.get("/settings", response_model=Settings)
def get_settings() -> Settings:
    return Settings(feedback_language=_get("feedback_language"))


@router.put("/settings", response_model=Settings)
def save_settings(body: Settings) -> Settings:
    with get_connection() as conn:
        if body.feedback_language is None:
            conn.execute("DELETE FROM settings WHERE key = 'feedback_language'")
        else:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES ('feedback_language', ?)",
                (body.feedback_language.strip(),),
            )
    return get_settings()

