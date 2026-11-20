"""SQLite access and seed data."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"

SEED_QUESTIONS = [
    ("common", "Tell me about yourself."),
    ("common", "Why do you want to work here?"),
    ("common", "Why are you leaving your current job?"),
    ("common", "What are your greatest strengths?"),
    ("common", "What is your biggest weakness?"),
    ("common", "Tell me about a challenge you faced and how you handled it."),
    ("common", "Tell me about a time you disagreed with a teammate."),
    ("common", "Describe a project you are most proud of."),
    ("common", "Where do you see yourself in five years?"),
    ("common", "Do you have any questions for us?"),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                text TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.executemany(
            "INSERT OR IGNORE INTO questions (category, text) VALUES (?, ?)",
            SEED_QUESTIONS,
        )
