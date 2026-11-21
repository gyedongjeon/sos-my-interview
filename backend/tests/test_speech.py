"""Reading questions aloud: the voice model download, synthesis, and the clip cache."""

import io
import threading
import wave

import numpy as np
import pytest

from app import speech


class FakeKokoro:
    """Stands in for the voice model: half a second of silence per request."""

    calls: list[str] = []

    def __init__(self, model_path, voices_path):
        pass

    def create(self, text, voice, speed, lang):
        FakeKokoro.calls.append(f"{voice}: {text}")
        return np.zeros(12000, dtype=np.float32), 24000


@pytest.fixture
def voice_model(monkeypatch):
    """The model files are "downloaded" and loading them gives the fake model."""
    speech.TTS_DIR.mkdir(parents=True)
    for name in speech.MODEL_FILES:
        (speech.TTS_DIR / name).write_bytes(b"model")
    FakeKokoro.calls = []
    monkeypatch.setattr(speech, "Kokoro", FakeKokoro)
    return FakeKokoro


def test_question_is_rendered_as_wav(voice_model):
    audio = speech.synthesize("Tell me about yourself.")
    with wave.open(io.BytesIO(audio)) as clip:
        assert (clip.getnchannels(), clip.getsampwidth(), clip.getframerate()) == (1, 2, 24000)
        assert clip.getnframes() == 12000


def test_repeated_question_is_served_from_the_cache(voice_model):
    first = speech.synthesize("Tell me about yourself.")
    assert speech.synthesize("Tell me about yourself.") == first
    assert voice_model.calls == [f"{speech.DEFAULT_VOICE}: Tell me about yourself."]


def test_another_voice_does_not_reuse_the_cached_clip(voice_model, monkeypatch):
    speech.synthesize("Tell me about yourself.")
    monkeypatch.setenv("TTS_VOICE", "am_adam")
    speech.synthesize("Tell me about yourself.")
    assert voice_model.calls[-1] == "am_adam: Tell me about yourself."


def test_missing_model_is_downloaded_in_the_background(monkeypatch):
    started, release, downloads = threading.Event(), threading.Event(), []

    def download():
        downloads.append(1)
        started.set()
        release.wait(5)

    monkeypatch.setattr(speech, "_download_models", download)
    try:
        # The request fails at once instead of waiting for the download...
        with pytest.raises(RuntimeError, match="still downloading"):
            speech.synthesize("Tell me about yourself.")
        assert started.wait(5)
        # ...and asking again while it runs does not start a second download.
        with pytest.raises(RuntimeError, match="still downloading"):
            speech.synthesize("Why do you want to work here?")
        assert downloads == [1]
    finally:
        release.set()


def test_speech_endpoint_reports_the_download_so_the_ui_can_fall_back(client, monkeypatch):
    monkeypatch.setattr(speech, "_download_models", lambda: None)
    response = client.post("/api/speech", json={"text": "Tell me about yourself."})
    assert response.status_code == 502
    assert "still downloading" in response.json()["detail"]


def test_speech_endpoint_returns_audio(client, voice_model):
    response = client.post("/api/speech", json={"text": "Tell me about yourself."})
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    assert response.content.startswith(b"RIFF")


def test_download_saves_both_model_files_and_leaves_no_partial_file(monkeypatch):
    requested = []

    def urlopen(url, context=None):
        requested.append(url)
        return io.BytesIO(b"model-bytes")

    monkeypatch.setattr(speech.urllib.request, "urlopen", urlopen)
    speech._download_models()

    assert requested == [f"{speech.RELEASE_URL}/{name}" for name in speech.MODEL_FILES]
    assert sorted(p.name for p in speech.TTS_DIR.iterdir()) == sorted(speech.MODEL_FILES)
    assert (speech.TTS_DIR / speech.MODEL_FILES[0]).read_bytes() == b"model-bytes"


def test_download_skips_files_that_are_already_there(monkeypatch):
    speech.TTS_DIR.mkdir(parents=True)
    (speech.TTS_DIR / speech.MODEL_FILES[0]).write_bytes(b"kept")
    monkeypatch.setattr(speech.urllib.request, "urlopen", lambda url, context=None: io.BytesIO(b"new"))
    speech._download_models()
    assert (speech.TTS_DIR / speech.MODEL_FILES[0]).read_bytes() == b"kept"
    assert (speech.TTS_DIR / speech.MODEL_FILES[1]).read_bytes() == b"new"
