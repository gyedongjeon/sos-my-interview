"""Shared test setup: every test runs on its own empty data folder and never reaches the network."""

import os
import shutil
import tempfile
from pathlib import Path

# The app reads these when it is imported, so they are set before any `app` import.
_ROOT = Path(tempfile.mkdtemp(prefix="sos-my-interview-tests-"))
os.environ["SOS_MY_INTERVIEW_DATA_DIR"] = str(_ROOT / "data")
os.environ["SOS_MY_INTERVIEW_FRONTEND_DIST"] = str(_ROOT / "dist")
for _name in ("LLM_MODEL", "FEEDBACK_LANGUAGE", "TTS_VOICE"):
    os.environ.pop(_name, None)

import litellm  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import speech  # noqa: E402
from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.paths import DATA_DIR, FRONTEND_DIST  # noqa: E402


def _no_network(*args, **kwargs):
    raise AssertionError("A test tried to reach the network; mock the call instead.")


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    """A fresh database and data folder, with the LLM and downloads blocked unless mocked."""
    shutil.rmtree(DATA_DIR, ignore_errors=True)
    shutil.rmtree(FRONTEND_DIST, ignore_errors=True)
    init_db()
    monkeypatch.setattr(litellm, "completion", _no_network)
    monkeypatch.setattr(speech.urllib.request, "urlopen", _no_network)
    monkeypatch.setattr(speech, "_kokoro", None)
    monkeypatch.setattr(speech, "_download", None)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def feedback() -> dict:
    """A valid feedback payload, as the model would return it."""
    return {
        "english": {
            "grammar": 70,
            "vocabulary": 65,
            "naturalness": 60,
            "summary": "Clear, with some tense slips.",
            "corrections": [
                {"original": "I am work there", "improved": "I worked there", "explanation": "Past tense."}
            ],
        },
        "content": {
            "relevance": 80,
            "structure": 75,
            "specificity": 55,
            "summary": "On topic, light on numbers.",
            "strengths": ["Direct answer"],
            "improvements": ["Add a measurable result"],
        },
        "better_answer": "I worked there for three years and led the migration.",
    }
