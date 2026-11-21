"""A few requests to a real LLM, to catch what mocks cannot: a prompt the model no longer
follows, a changed provider API, a retired model name.

Left out of a normal run. With a key in `.env`:

    uv run --env-file .env pytest -m live

Replies differ every time, so these tests check the shape of a reply, never its wording.
"""

import re

import pytest

pytestmark = pytest.mark.live

TURNS = [
    {
        "question": "Tell me about yourself.",
        "answer": (
            "I am backend engineer with five year experience. I worked at a payment company and "
            "I make the API faster, and now I looking for new challenge in bigger team."
        ),
    }
]
POSTING = {
    "title": "Backend Engineer at Acme",
    "text": (
        "Acme builds payment infrastructure. We are hiring a backend engineer to design and run "
        "high-volume payment APIs in Python, work with PostgreSQL, and take part in on-call. "
        "You have several years of experience building reliable services."
    ),
}


def test_follow_up_is_one_short_question(client):
    response = client.post("/api/follow-up", json={"turns": TURNS, "question_id": 1})
    assert response.status_code == 200, response.text
    question = response.json()["question"]
    assert 5 <= len(question) <= 400
    assert "\n" not in question


def test_feedback_follows_the_schema_and_the_chosen_language(client):
    client.put("/api/settings", json={"feedback_language": "Korean"})
    response = client.post("/api/evaluate", json={"turns": TURNS, "question_id": 1})
    # A reply that does not match the Feedback schema is reported as 502 by the endpoint.
    assert response.status_code == 200, response.text
    feedback = response.json()
    scores = [feedback["english"][k] for k in ("grammar", "vocabulary", "naturalness")]
    scores += [feedback["content"][k] for k in ("relevance", "structure", "specificity")]
    assert all(isinstance(score, int) and 0 <= score <= 100 for score in scores)
    assert feedback["better_answer"].strip()
    # The explanation is written in the chosen language; the better answer stays in English.
    assert re.search("[가-힣]", feedback["english"]["summary"] + feedback["content"]["summary"])
    assert not re.search("[가-힣]", feedback["better_answer"])


def test_questions_are_written_for_a_job_posting(client):
    response = client.post("/api/postings", json=POSTING)
    assert response.status_code == 201, response.text
    posting = response.json()
    assert posting["warning"] is None
    assert posting["question_count"] >= 3
    questions = [q["text"] for q in client.get("/api/questions").json() if q["posting_id"] == posting["id"]]
    assert all(len(text) >= 10 for text in questions)
