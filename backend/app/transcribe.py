"""Local speech-to-text with Whisper (faster-whisper); no API key, audio stays on this machine."""

import os
import threading
from typing import BinaryIO

from faster_whisper import WhisperModel

# English-only model, downloaded from Hugging Face on first use (~480 MB for small.en).
DEFAULT_MODEL = "small.en"

_model: WhisperModel | None = None
_lock = threading.Lock()


def _get_model() -> WhisperModel:
    global _model
    with _lock:
        if _model is None:
            name = os.environ.get("WHISPER_MODEL", "").strip() or DEFAULT_MODEL
            _model = WhisperModel(name, device="cpu", compute_type="int8")
        return _model


def transcribe(audio: BinaryIO) -> str:
    """Return the spoken text of an audio (or video) file, or "" if there is no speech."""
    model = _get_model()
    # The model is not safe for concurrent use; requests are rare, so run one at a time.
    with _lock:
        # vad_filter drops silence, which otherwise makes Whisper invent text.
        segments, _ = model.transcribe(audio, language="en", vad_filter=True)
        return " ".join(segment.text.strip() for segment in segments).strip()
