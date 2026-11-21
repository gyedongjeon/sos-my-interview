"""Follow-up questions and scored feedback, with the model's reply prepared by the test."""

import json

import pytest

from app import evaluate, follow_up
from app.llm import LLMError

TURNS = [{"question": "Tell me about yourself.", "answer": "I build payment systems."}]


@pytest.fixture
def model(monkeypatch):
    """Records what is sent to the model and replies with `model.reply`."""

    def complete(system, user, **params):
        complete.system, complete.user = system, user
        if isinstance(complete.reply, Exception):
            raise complete.reply
        return complete.reply

    complete.reply = ""
    monkeypatch.setattr(follow_up, "complete", complete)
    monkeypatch.setattr(evaluate, "complete", complete)
    return complete


def test_follow_up_is_asked_about_the_interview_so_far(client, model):
    model.reply = "Which payment system was the hardest to build?"
    client.put("/api/resume", data={"text": "Ten years at a bank."})
    response = client.post("/api/follow-up", json={"turns": TURNS, "question_id": 1})
    assert response.json() == {"question": "Which payment system was the hardest to build?"}
    assert "<resume>\nTen years at a bank.\n</resume>" in model.user
    assert "Interviewer: Tell me about yourself.\nCandidate: I build payment systems." in model.user


def test_follow_up_reports_a_model_failure(client, model):
    model.reply = LLMError("The LLM provider's rate limit was reached. Try again shortly.")
    response = client.post("/api/follow-up", json={"turns": TURNS})
    assert response.status_code == 502
    assert "rate limit" in response.json()["detail"]


def test_follow_up_needs_an_answered_question(client, model):
    assert client.post("/api/follow-up", json={"turns": []}).status_code == 422
    assert client.post("/api/follow-up", json={"turns": [{"question": "Q", "answer": ""}]}).status_code == 422


def test_feedback_is_scored_in_the_chosen_language(client, model, feedback):
    model.reply = json.dumps(feedback)
    client.put("/api/settings", json={"feedback_language": "Korean"})
    response = client.post("/api/evaluate", json={"turns": TURNS, "question_id": 1})
    assert response.json() == feedback
    assert "Korean" in model.system


def test_feedback_outside_the_score_range_is_rejected(client, model, feedback):
    feedback["english"]["grammar"] = 140
    model.reply = json.dumps(feedback)
    response = client.post("/api/evaluate", json={"turns": TURNS})
    assert response.status_code == 502
    assert "unexpected format" in response.json()["detail"]


def test_speaking_feedback_needs_one_question_and_transcript_per_clip(client):
    response = client.post(
        "/api/evaluate/speaking",
        files=[("files", ("a.webm", b"x", "video/webm"))],
        data={"questions": ["Q1", "Q2"], "transcripts": ["A1"]},
    )
    assert response.status_code == 422

