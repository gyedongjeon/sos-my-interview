"""The candidate's background: their résumé and the job postings they are preparing for."""

import io
import json
from datetime import datetime, timezone
from html import unescape
from typing import Literal

import lxml.html
import trafilatura
from fastapi import APIRouter, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from pypdf import PdfReader

from .db import get_connection
from .llm import LLMError
from .tailored import Difficulty, generate_questions

# Upper bound on what is stored and sent to the LLM per document.
MAX_CHARS = 20_000

router = APIRouter(prefix="/api")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- Résumé ---------------------------------------------------------------------------


class Resume(BaseModel):
    filename: str | None
    text: str
    updated_at: str


def _read_document(file: UploadFile) -> str:
    """Extract the text of an uploaded résumé or cover letter."""
    name = (file.filename or "").lower()
    data = file.file.read()
    if name.endswith(".pdf"):
        try:
            pages = PdfReader(io.BytesIO(data)).pages
            return "\n\n".join(page.extract_text() or "" for page in pages)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Could not read the PDF: {e}") from e
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="replace")
    raise HTTPException(status_code=422, detail="Upload a PDF, .txt, or .md file, or paste the text.")


def _document_text(file: UploadFile | None, text: str) -> str:
    """Text of an uploaded file, or of the pasted text when there is no file."""
    content = (_read_document(file) if file else text).strip()
    if not content:
        detail = (
            "No text could be extracted from the file. If it is a scanned PDF, paste the text instead."
            if file
            else "The text is empty."
        )
        raise HTTPException(status_code=422, detail=detail)
    return content[:MAX_CHARS]


@router.get("/resume", response_model=Resume | None)
def get_resume() -> Resume | None:
    with get_connection() as conn:
        row = conn.execute("SELECT filename, text, updated_at FROM resume WHERE id = 1").fetchone()
    return Resume(**dict(row)) if row else None


@router.put("/resume", response_model=Resume)
def save_resume(file: UploadFile | None = None, text: str = Form("")) -> Resume:
    """Replace the résumé with an uploaded file (text is extracted) or with pasted text."""
    content = _document_text(file, text)
    resume = Resume(filename=file.filename if file else None, text=content, updated_at=_now())
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO resume (id, filename, text, updated_at) VALUES (1, ?, ?, ?)",
            (resume.filename, resume.text, resume.updated_at),
        )
    return resume


@router.delete("/resume", status_code=204)
def delete_resume() -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM resume")


# --- Job postings ---------------------------------------------------------------------


class Posting(BaseModel):
    id: int
    title: str
    url: str | None
    text: str
    created_at: str
    # Documents written for this posting. Without a résumé here, the common one is used.
    resume_text: str | None = None
    resume_filename: str | None = None
    cover_letter_text: str | None = None
    cover_letter_filename: str | None = None
    question_count: int = 0
    # Set when the posting was saved but its questions could not be generated.
    warning: str | None = None


class PostingCreate(BaseModel):
    """Give a URL to extract the posting from the page, or paste its text (or both)."""

    url: str | None = Field(default=None, max_length=2000)
    text: str = ""
    title: str = Field(default="", max_length=200)
    difficulty: Difficulty = "standard"


class PostingUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1)


def _html_to_text(fragment: str) -> str:
    """Plain text of an HTML fragment, one line per block element."""
    root = lxml.html.fromstring(f"<div>{fragment}</div>")
    for element in root.iter("p", "li", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "tr"):
        prefix = "- " if element.tag == "li" else ""
        element.text = f"\n{prefix}{element.text or ''}"
        if element.tag == "br":
            element.tail = f"\n{element.tail or ''}"
    lines = (line.strip() for line in root.text_content().splitlines())
    return "\n".join(line for line in lines if line and line != "-")


def _find_job_posting(node) -> dict | None:
    """Find a schema.org JobPosting object anywhere inside parsed JSON-LD."""
    if isinstance(node, dict):
        kind = node.get("@type")
        if kind == "JobPosting" or (isinstance(kind, list) and "JobPosting" in kind):
            return node
        node = list(node.values())
    if isinstance(node, list):
        for child in node:
            if found := _find_job_posting(child):
                return found
    return None


def _extract_structured(html: str) -> tuple[str, str] | None:
    """Read the posting from the page's embedded JSON-LD, if it has one.

    Job boards (Ashby, Greenhouse, Lever, ...) embed a schema.org JobPosting for search
    engines, even when the visible page is rendered with JavaScript.
    """
    for script in lxml.html.fromstring(html).xpath('//script[@type="application/ld+json"]/text()'):
        try:
            posting = _find_job_posting(json.loads(script))
        except ValueError:
            continue
        if not posting or not isinstance(posting.get("description"), str):
            continue
        # Some sites HTML-escape the description inside the JSON.
        text = _html_to_text(unescape(posting["description"]))
        title = str(posting.get("title") or "").strip()
        organization = posting.get("hiringOrganization")
        company = str(organization.get("name") or "").strip() if isinstance(organization, dict) else ""
        return (f"{title} at {company}" if title and company else title or company), text
    return None


def _extract_from_url(url: str) -> tuple[str, str]:
    """Return (title, posting text) of a web page."""
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=422, detail="The link must start with http:// or https://.")
    html = trafilatura.fetch_url(url)
    title, text = "", ""
    if html:
        if structured := _extract_structured(html):
            title, text = structured
        else:
            # No structured data: fall back to the page's main readable text.
            extracted = trafilatura.extract(html, output_format="json", with_metadata=True)
            data = json.loads(extracted) if extracted else {}
            title, text = (data.get("title") or "").strip(), (data.get("text") or "").strip()
    if len(text) < 200:
        # Typical for pages that need a login or render their content with JavaScript.
        raise HTTPException(
            status_code=422,
            detail="Could not extract the posting from this link. Paste the posting text instead.",
        )
    return title, text


POSTING_SQL = """
    SELECT p.*, (SELECT COUNT(*) FROM questions q WHERE q.posting_id = p.id) AS question_count
    FROM job_postings p
"""


def _get_posting(conn, posting_id: int) -> Posting:
    row = conn.execute(POSTING_SQL + " WHERE p.id = ?", (posting_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Job posting not found.")
    return Posting(**dict(row))


def _resume_for(conn, posting: Posting) -> str | None:
    """The résumé to use for a posting: its own if it has one, else the common résumé."""
    if posting.resume_text:
        return posting.resume_text
    row = conn.execute("SELECT text FROM resume WHERE id = 1").fetchone()
    return row["text"] if row else None


def _remove_questions(conn, posting_id: int) -> None:
    """Drop a posting's questions, keeping (archived) the ones that already have answers."""
    conn.execute(
        """
        UPDATE questions SET category = 'archived', posting_id = NULL
        WHERE posting_id = ? AND id IN (SELECT question_id FROM attempts)
        """,
        (posting_id,),
    )
    conn.execute("DELETE FROM questions WHERE posting_id = ?", (posting_id,))


def _generate_questions(posting_id: int, difficulty: Difficulty) -> Posting:
    """Replace a posting's questions with newly generated ones. Raises LLMError."""
    with get_connection() as conn:
        posting = _get_posting(conn, posting_id)
        resume = _resume_for(conn, posting)
    # The model call takes seconds; do it outside the database transaction.
    questions = generate_questions(
        posting.title, posting.text, resume, posting.cover_letter_text, difficulty
    )
    with get_connection() as conn:
        _remove_questions(conn, posting_id)
        conn.executemany(
            "INSERT OR IGNORE INTO questions (category, text, posting_id) VALUES ('tailored', ?, ?)",
            [(question, posting_id) for question in questions],
        )
        return _get_posting(conn, posting_id)


@router.get("/postings", response_model=list[Posting])
def list_postings() -> list[Posting]:
    with get_connection() as conn:
        rows = conn.execute(POSTING_SQL + " ORDER BY p.id DESC").fetchall()
    return [Posting(**dict(row)) for row in rows]


@router.get("/postings/{posting_id}", response_model=Posting)
def get_posting(posting_id: int) -> Posting:
    with get_connection() as conn:
        return _get_posting(conn, posting_id)


@router.post("/postings", response_model=Posting, status_code=201)
def create_posting(body: PostingCreate) -> Posting:
    url = (body.url or "").strip() or None
    text = body.text.strip()
    title = body.title.strip()
    if not text:
        if not url:
            raise HTTPException(status_code=422, detail="Give a link or paste the posting text.")
        page_title, text = _extract_from_url(url)
        title = title or page_title
    title = title or "Untitled posting"
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO job_postings (title, url, text, created_at) VALUES (?, ?, ?, ?)",
            (title[:200], url, text[:MAX_CHARS], _now()),
        )
        posting = _get_posting(conn, cursor.lastrowid)
    try:
        return _generate_questions(posting.id, body.difficulty)
    except LLMError as e:
        posting.warning = f"The posting was saved, but its questions could not be generated: {e}"
        return posting


@router.post("/postings/{posting_id}/questions", response_model=Posting)
def regenerate_questions(posting_id: int, difficulty: Difficulty = "standard") -> Posting:
    """Generate a new set of tailored questions for a posting, replacing the old set."""
    try:
        return _generate_questions(posting_id, difficulty)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e


@router.put("/postings/{posting_id}", response_model=Posting)
def update_posting(posting_id: int, body: PostingUpdate) -> Posting:
    with get_connection() as conn:
        _get_posting(conn, posting_id)
        conn.execute(
            "UPDATE job_postings SET title = ?, text = ? WHERE id = ?",
            (body.title.strip(), body.text.strip()[:MAX_CHARS], posting_id),
        )
        return _get_posting(conn, posting_id)


DocumentKind = Literal["resume", "cover_letter"]


@router.put("/postings/{posting_id}/documents/{kind}", response_model=Posting)
def save_posting_document(
    posting_id: int, kind: DocumentKind, file: UploadFile | None = None, text: str = Form("")
) -> Posting:
    """Set the résumé or cover letter written for this posting, from a file or pasted text."""
    content = _document_text(file, text)
    with get_connection() as conn:
        _get_posting(conn, posting_id)
        # `kind` is validated against DocumentKind, so it is safe to use in column names.
        conn.execute(
            f"UPDATE job_postings SET {kind}_text = ?, {kind}_filename = ? WHERE id = ?",
            (content, file.filename if file else None, posting_id),
        )
        return _get_posting(conn, posting_id)


@router.delete("/postings/{posting_id}/documents/{kind}", response_model=Posting)
def delete_posting_document(posting_id: int, kind: DocumentKind) -> Posting:
    """Remove a posting's own résumé (falling back to the common one) or its cover letter."""
    with get_connection() as conn:
        _get_posting(conn, posting_id)
        conn.execute(
            f"UPDATE job_postings SET {kind}_text = NULL, {kind}_filename = NULL WHERE id = ?",
            (posting_id,),
        )
        return _get_posting(conn, posting_id)


@router.delete("/postings/{posting_id}", status_code=204)
def delete_posting(posting_id: int) -> None:
    with get_connection() as conn:
        _get_posting(conn, posting_id)
        _remove_questions(conn, posting_id)
        conn.execute("DELETE FROM job_postings WHERE id = ?", (posting_id,))


# --- Prompt context -------------------------------------------------------------------


def candidate_background(question_id: int | None = None) -> str:
    """The candidate's documents and the job posting a question was written for, as a prompt section.

    A posting's own résumé replaces the common one. Returns "" when nothing is set; common
    questions have no posting, so they get the common résumé only.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT p.id FROM job_postings p JOIN questions q ON q.posting_id = p.id WHERE q.id = ?",
            (question_id,),
        ).fetchone()
        posting = _get_posting(conn, row["id"]) if row else None
        if posting:
            resume = _resume_for(conn, posting)
        else:
            common = conn.execute("SELECT text FROM resume WHERE id = 1").fetchone()
            resume = common["text"] if common else None
    sections = []
    if posting:
        sections.append(f"<job_posting title={posting.title!r}>\n{posting.text}\n</job_posting>")
    if resume:
        sections.append(f"<resume>\n{resume}\n</resume>")
    if posting and posting.cover_letter_text:
        sections.append(f"<cover_letter>\n{posting.cover_letter_text}\n</cover_letter>")
    return "\n\n".join(sections)
