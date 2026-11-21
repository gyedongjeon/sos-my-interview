"""Saved attempts: answers, recordings, scores, and feedback."""

from app.attempts import RECORDINGS_DIR


def start_attempt(client, question_id: int = 1) -> int:
    return client.post("/api/attempts", json={"question_id": question_id}).json()["id"]


def answer(client, attempt_id: int, **fields):
    data = {"question": "Tell me about yourself.", "answer": "I build things.", **fields}
    return client.post(f"/api/attempts/{attempt_id}/turns", data=data)


def test_attempt_for_an_unknown_question_is_rejected(client):
    assert client.post("/api/attempts", json={"question_id": 999}).status_code == 404


def test_attempts_without_answers_are_not_listed(client):
    start_attempt(client)
    assert client.get("/api/attempts").json() == []


def test_answers_are_numbered_in_order(client):
    attempt_id = start_attempt(client)
    assert answer(client, attempt_id).json() == {"position": 1}
    assert answer(client, attempt_id, question="Why?", answer="Because.").json() == {"position": 2}

    detail = client.get(f"/api/attempts/{attempt_id}").json()
    assert [(t["position"], t["question"], t["answer"]) for t in detail["turns"]] == [
        (1, "Tell me about yourself.", "I build things."),
        (2, "Why?", "Because."),
    ]
    assert detail["question"] == "Tell me about yourself."
    assert detail["posting_title"] is None
    assert detail["feedback"] is None


def test_delivery_details_are_saved_with_the_answer(client):
    attempt_id = start_attempt(client)
    answer(client, attempt_id, clarity=82, unclear_words='["migration"]', words_per_minute=130)
    turn = client.get(f"/api/attempts/{attempt_id}").json()["turns"][0]
    assert (turn["clarity"], turn["unclear_words"], turn["words_per_minute"]) == (82, ["migration"], 130)


def test_unclear_words_must_be_a_json_list(client):
    attempt_id = start_attempt(client)
    assert answer(client, attempt_id, unclear_words="{}").status_code == 422
    assert answer(client, attempt_id, unclear_words="not json").status_code == 422


def test_newest_attempt_is_listed_first(client):
    first, second = start_attempt(client, 1), start_attempt(client, 2)
    answer(client, first)
    answer(client, second)
    assert [a["id"] for a in client.get("/api/attempts").json()] == [second, first]


def test_recording_is_stored_and_played_back(client):
    attempt_id = start_attempt(client)
    client.post(
        f"/api/attempts/{attempt_id}/turns",
        data={"question": "Q", "answer": "A", "has_video": "true"},
        files={"recording": ("answer.webm", b"webm-bytes", "video/webm")},
    )
    turn = client.get(f"/api/attempts/{attempt_id}").json()["turns"][0]
    assert turn["has_video"] is True
    recording = client.get(turn["recording_url"])
    assert recording.content == b"webm-bytes"
    assert recording.headers["content-type"] == "video/webm"


def test_answer_without_a_recording_has_no_recording_url(client):
    attempt_id = start_attempt(client)
    answer(client, attempt_id)
    assert client.get(f"/api/attempts/{attempt_id}").json()["turns"][0]["recording_url"] is None
    assert client.get(f"/api/attempts/{attempt_id}/recordings/1").status_code == 404


def test_feedback_and_scores_are_saved(client, feedback):
    attempt_id = start_attempt(client)
    answer(client, attempt_id)
    body = {"feedback": feedback, "english_score": 65, "content_score": 70}
    assert client.put(f"/api/attempts/{attempt_id}/feedback", json=body).status_code == 204

    detail = client.get(f"/api/attempts/{attempt_id}").json()
    assert detail["feedback"] == feedback
    assert detail["speaking"] is None
    summary = client.get("/api/attempts").json()[0]
    assert (summary["english_score"], summary["content_score"]) == (65, 70)


def test_scores_must_be_between_0_and_100(client, feedback):
    attempt_id = start_attempt(client)
    body = {"feedback": feedback, "english_score": 101, "content_score": 70}
    assert client.put(f"/api/attempts/{attempt_id}/feedback", json=body).status_code == 422


def test_deleting_an_attempt_removes_its_answers_and_recordings(client):
    attempt_id = start_attempt(client)
    client.post(
        f"/api/attempts/{attempt_id}/turns",
        data={"question": "Q", "answer": "A"},
        files={"recording": ("answer.webm", b"webm-bytes", "video/webm")},
    )
    assert (RECORDINGS_DIR / str(attempt_id) / "1.webm").is_file()

    assert client.delete(f"/api/attempts/{attempt_id}").status_code == 204
    assert client.get(f"/api/attempts/{attempt_id}").status_code == 404
    assert client.get("/api/attempts").json() == []
    assert not (RECORDINGS_DIR / str(attempt_id)).exists()


def test_unknown_attempt_is_not_found(client, feedback):
    assert client.get("/api/attempts/999").status_code == 404
    assert answer(client, 999).status_code == 404
    assert client.delete("/api/attempts/999").status_code == 404
