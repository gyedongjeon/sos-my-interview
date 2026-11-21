"""Résumé, job postings, tailored questions, and the context given to the model."""

import pytest

from app import background
from app.background import MAX_CHARS, _extract_structured, _html_to_text, candidate_background
from app.llm import LLMError

POSTING = {"title": "Backend Engineer at Acme", "text": "Build and run our payment APIs."}


@pytest.fixture
def questions(monkeypatch):
    """Stand in for the model: each call returns the next prepared list of questions."""
    calls = []
    replies = [["How would you design a payment API?", "Tell me about an outage you handled."]]

    def generate(title, posting, resume, cover_letter=None, difficulty="standard"):
        calls.append({"title": title, "resume": resume, "cover_letter": cover_letter, "difficulty": difficulty})
        return replies[min(len(calls), len(replies)) - 1]

    monkeypatch.setattr(background, "generate_questions", generate)
    generate.calls, generate.replies = calls, replies
    return generate


def add_posting(client, **fields) -> dict:
    return client.post("/api/postings", json={**POSTING, **fields}).json()


# --- Résumé ---------------------------------------------------------------------------


def test_resume_is_empty_at_first(client):
    assert client.get("/api/resume").json() is None


def test_pasted_resume_is_saved_and_removed(client):
    saved = client.put("/api/resume", data={"text": "  Ten years of backend work.  "}).json()
    assert (saved["filename"], saved["text"]) == (None, "Ten years of backend work.")
    assert client.get("/api/resume").json() == saved
    assert client.delete("/api/resume").status_code == 204
    assert client.get("/api/resume").json() is None


def test_uploaded_text_file_keeps_its_name(client):
    saved = client.put("/api/resume", files={"file": ("cv.md", "# Me\nBackend".encode(), "text/markdown")}).json()
    assert (saved["filename"], saved["text"]) == ("cv.md", "# Me\nBackend")


def test_resume_is_cut_at_the_size_limit(client):
    saved = client.put("/api/resume", data={"text": "a" * (MAX_CHARS + 10)}).json()
    assert len(saved["text"]) == MAX_CHARS


@pytest.mark.parametrize(
    "request_kwargs",
    [
        {"data": {"text": "   "}},
        {"files": {"file": ("cv.docx", b"binary", "application/octet-stream")}},
        {"files": {"file": ("cv.pdf", b"not a pdf", "application/pdf")}},
        {"files": {"file": ("cv.txt", b"   ", "text/plain")}},
    ],
)
def test_unreadable_resume_is_rejected(client, request_kwargs):
    assert client.put("/api/resume", **request_kwargs).status_code == 422
    assert client.get("/api/resume").json() is None


# --- Job postings ---------------------------------------------------------------------


def test_posting_gets_tailored_questions(client, questions):
    posting = add_posting(client, difficulty="hard")
    assert posting["question_count"] == 2
    assert posting["warning"] is None
    assert questions.calls[0]["difficulty"] == "hard"

    tailored = [q for q in client.get("/api/questions").json() if q["posting_id"] == posting["id"]]
    assert [q["text"] for q in tailored] == questions.replies[0]
    assert all(q["category"] == "tailored" for q in tailored)


def test_posting_is_kept_when_questions_cannot_be_generated(client, monkeypatch):
    def fail(*args, **kwargs):
        raise LLMError("No model is configured.")

    monkeypatch.setattr(background, "generate_questions", fail)
    response = client.post("/api/postings", json=POSTING)
    assert response.status_code == 201
    assert "No model is configured." in response.json()["warning"]
    assert [p["title"] for p in client.get("/api/postings").json()] == [POSTING["title"]]


def test_posting_needs_text_or_a_link(client, questions):
    assert client.post("/api/postings", json={"title": "Empty"}).status_code == 422
    assert client.post("/api/postings", json={"url": "ftp://example.com/job"}).status_code == 422
    assert client.get("/api/postings").json() == []


def test_posting_from_a_link_uses_the_page_title(client, questions, monkeypatch):
    monkeypatch.setattr(background, "_extract_from_url", lambda url: ("Data Engineer at Globex", "Own the pipelines."))
    posting = client.post("/api/postings", json={"url": " https://example.com/job "}).json()
    assert (posting["title"], posting["url"], posting["text"]) == (
        "Data Engineer at Globex",
        "https://example.com/job",
        "Own the pipelines.",
    )


def test_untitled_posting_gets_a_placeholder_title(client, questions):
    assert client.post("/api/postings", json={"text": "Some job."}).json()["title"] == "Untitled posting"


def test_regenerating_replaces_unanswered_questions_and_archives_answered_ones(client, questions):
    posting = add_posting(client)
    answered, unanswered = [q for q in client.get("/api/questions").json() if q["posting_id"] == posting["id"]]
    attempt_id = client.post("/api/attempts", json={"question_id": answered["id"]}).json()["id"]
    client.post(f"/api/attempts/{attempt_id}/turns", data={"question": answered["text"], "answer": "A"})

    questions.replies.append(["What would you change about our API?"])
    regenerated = client.post(f"/api/postings/{posting['id']}/questions").json()
    assert regenerated["question_count"] == 1

    listed = {q["text"] for q in client.get("/api/questions").json()}
    assert "What would you change about our API?" in listed
    assert answered["text"] not in listed and unanswered["text"] not in listed
    # The answered question is archived, not deleted, so its history survives.
    assert client.get(f"/api/attempts/{attempt_id}").json()["question"] == answered["text"]


def test_regenerating_reports_a_model_failure(client, questions, monkeypatch):
    posting = add_posting(client)

    def fail(*args, **kwargs):
        raise LLMError("rate limit")

    monkeypatch.setattr(background, "generate_questions", fail)
    response = client.post(f"/api/postings/{posting['id']}/questions")
    assert response.status_code == 502
    assert client.get(f"/api/postings/{posting['id']}").json()["question_count"] == 2


def test_posting_is_edited(client, questions):
    posting = add_posting(client)
    updated = client.put(f"/api/postings/{posting['id']}", json={"title": " Staff Engineer ", "text": " New text "}).json()
    assert (updated["title"], updated["text"]) == ("Staff Engineer", "New text")


def test_posting_resume_replaces_the_common_one_for_its_questions(client, questions):
    client.put("/api/resume", data={"text": "Common résumé"})
    posting = add_posting(client)
    assert questions.calls[-1]["resume"] == "Common résumé"

    url = f"/api/postings/{posting['id']}/documents"
    client.put(f"{url}/resume", data={"text": "Résumé for Acme"})
    client.put(f"{url}/cover_letter", data={"text": "Dear Acme"})
    client.post(f"/api/postings/{posting['id']}/questions")
    assert (questions.calls[-1]["resume"], questions.calls[-1]["cover_letter"]) == ("Résumé for Acme", "Dear Acme")

    cleared = client.delete(f"{url}/resume").json()
    assert cleared["resume_text"] is None and cleared["cover_letter_text"] == "Dear Acme"
    assert client.put(f"{url}/portfolio", data={"text": "x"}).status_code == 422


def test_deleting_a_posting_removes_its_questions(client, questions):
    posting = add_posting(client)
    assert client.delete(f"/api/postings/{posting['id']}").status_code == 204
    assert client.get(f"/api/postings/{posting['id']}").status_code == 404
    assert all(q["posting_id"] is None for q in client.get("/api/questions").json())


# --- Context for the model ------------------------------------------------------------


def test_common_question_gets_only_the_common_resume(client):
    assert candidate_background(1) == ""
    client.put("/api/resume", data={"text": "Common résumé"})
    assert candidate_background(1) == "<resume>\nCommon résumé\n</resume>"


def test_tailored_question_gets_its_posting_and_documents(client, questions):
    client.put("/api/resume", data={"text": "Common résumé"})
    posting = add_posting(client)
    client.put(f"/api/postings/{posting['id']}/documents/cover_letter", data={"text": "Dear Acme"})
    question_id = next(q["id"] for q in client.get("/api/questions").json() if q["posting_id"] == posting["id"])

    context = candidate_background(question_id)
    assert context.startswith("<job_posting title='Backend Engineer at Acme'>\nBuild and run our payment APIs.")
    assert "<resume>\nCommon résumé\n</resume>" in context
    assert context.endswith("<cover_letter>\nDear Acme\n</cover_letter>")


# --- Reading a posting from a web page ------------------------------------------------


def test_html_becomes_one_line_per_block():
    html = "<h2>About</h2><p>We build <b>APIs</b>.</p><ul><li>Python</li><li>SQL</li></ul>"
    assert _html_to_text(html) == "About\nWe build APIs.\n- Python\n- SQL"


def test_posting_is_read_from_structured_data():
    page = """<html><head><script type="application/ld+json">
    {"@graph": [{"@type": "WebSite"}, {"@type": "JobPosting", "title": "Backend Engineer",
      "hiringOrganization": {"name": "Acme"}, "description": "&lt;p&gt;Run the APIs.&lt;/p&gt;"}]}
    </script></head><body></body></html>"""
    assert _extract_structured(page) == ("Backend Engineer at Acme", "Run the APIs.")


def test_page_without_a_job_posting_has_no_structured_data():
    page = '<html><head><script type="application/ld+json">{"@type": "WebSite"}</script></head><body>x</body></html>'
    assert _extract_structured(page) is None
