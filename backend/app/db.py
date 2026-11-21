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
    conn.execute("PRAGMA foreign_keys = ON")
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
        # Tailored questions belong to a job posting; common ones have no posting.
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(questions)")}
        if "posting_id" not in columns:
            conn.execute("ALTER TABLE questions ADD COLUMN posting_id INTEGER")
        # The single user's résumé: at most one row.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resume (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                filename TEXT,
                text TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        # Job postings the user is preparing for; each has its own tailored questions.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS job_postings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        # Application documents written for one posting; NULL means "not set" (the common
        # résumé is used, and there is no cover letter).
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(job_postings)")}
        for column in ("resume_text", "resume_filename", "cover_letter_text", "cover_letter_filename"):
            if column not in columns:
                conn.execute(f"ALTER TABLE job_postings ADD COLUMN {column} TEXT")
        # One attempt = answering one question once, including its follow-ups.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL REFERENCES questions(id),
                created_at TEXT NOT NULL,
                english_score INTEGER,
                content_score INTEGER,
                feedback TEXT,
                speaking TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS attempt_turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempt_id INTEGER NOT NULL REFERENCES attempts(id) ON DELETE CASCADE,
                position INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                clarity INTEGER,
                unclear_words TEXT NOT NULL DEFAULT '[]',
                words_per_minute INTEGER,
                recording TEXT,
                has_video INTEGER NOT NULL DEFAULT 0,
                UNIQUE (attempt_id, position)
            )
            """
        )
