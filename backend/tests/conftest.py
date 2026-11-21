"""Shared test setup: every test runs on its own empty data folder and never reaches the network."""

import os
import shutil
import tempfile
from pathlib import Path

# The app reads these when it is imported, so they are set before any `app` import.
_ROOT = Path(tempfile.mkdtemp(prefix="sos-my-interview-tests-"))
os.environ["SOS_MY_INTERVIEW_DATA_DIR"] = str(_ROOT / "data")
os.environ["SOS_MY_INTERVIEW_FRONTEND_DIST"] = str(_ROOT / "dist")
# LiteLLM loads a `.env` file from the working folder when it is imported, unless it is told it
# runs in production. Tests must not depend on what a developer keeps in `backend/.env`.
os.environ["LITELLM_MODE"] = "PRODUCTION"
# The model for the tests that call a real LLM (`-m live`); every other test runs without one.
LIVE_MODEL = os.environ.get("LLM_MODEL", "").strip() or "gemini/gemini-3.1-flash-lite"
for _name in ("LLM_MODEL", "FEEDBACK_LANGUAGE", "TTS_VOICE"):
    os.environ.pop(_name, None)

import litellm  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import speech, transcribe  # noqa: E402
from app.db import init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.paths import DATA_DIR, FRONTEND_DIST  # noqa: E402


def _no_network(*args, **kwargs):
    raise AssertionError("A test tried to reach the network; mock the call instead.")


# The environment variable LiteLLM reads the API key from, by provider.
KEY_VARIABLES = {
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


@pytest.fixture(autouse=True)
def isolated(monkeypatch, request):
    """A fresh database and data folder, with the LLM and downloads blocked unless mocked."""
    shutil.rmtree(DATA_DIR, ignore_errors=True)
    shutil.rmtree(FRONTEND_DIST, ignore_errors=True)
    init_db()
    if request.node.get_closest_marker("live"):
        # The one kind of test that is allowed to reach a real model.
        variable = KEY_VARIABLES.get(LIVE_MODEL.split("/")[0])
        if not variable or not os.environ.get(variable, "").strip():
            pytest.skip(f"No API key for {LIVE_MODEL}: set {variable or 'the provider key'} to run the live tests.")
        monkeypatch.setenv("LLM_MODEL", LIVE_MODEL)
    else:
        monkeypatch.setattr(litellm, "completion", _no_network)
    monkeypatch.setattr(speech.urllib.request, "urlopen", _no_network)
    monkeypatch.setattr(speech, "_kokoro", None)
    monkeypatch.setattr(transcribe, "_download", _no_network)
    for download in (speech.model_download, transcribe.model_download):
        monkeypatch.setattr(download, "_thread", None)
        monkeypatch.setattr(download, "error", None)


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
