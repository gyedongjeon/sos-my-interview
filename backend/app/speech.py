"""Local text-to-speech with Kokoro (kokoro-onnx); no API key, runs on this machine."""

import hashlib
import io
import os
import shutil
import ssl
import threading
import urllib.request
import wave

import certifi
import numpy as np
from kokoro_onnx import Kokoro

from .paths import DATA_DIR

TTS_DIR = DATA_DIR / "tts"
CACHE_DIR = TTS_DIR / "cache"
# Model files (~350 MB in total), downloaded on first use.
RELEASE_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
MODEL_FILES = ("kokoro-v1.0.onnx", "voices-v1.0.bin")
DEFAULT_VOICE = "af_heart"

_kokoro: Kokoro | None = None
_download: threading.Thread | None = None
_lock = threading.Lock()


def _download_models() -> None:
    TTS_DIR.mkdir(parents=True, exist_ok=True)
    for name in MODEL_FILES:
        path = TTS_DIR / name
        if not path.exists():
            # Download to a temporary name so an interrupted download is not reused.
            partial = path.with_suffix(path.suffix + ".part")
            # certifi's CA bundle: some Python installs ship without root certificates.
            tls = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(f"{RELEASE_URL}/{name}", context=tls) as response:
                with partial.open("wb") as out:
                    shutil.copyfileobj(response, out)
            partial.rename(path)


def _get_kokoro() -> Kokoro:
    """Return the loaded voice model. Raises while its files are still being downloaded."""
    global _kokoro, _download
    if _kokoro is None:
        if not all((TTS_DIR / name).exists() for name in MODEL_FILES):
            # The download takes minutes, so it runs in the background instead of holding the
            # request; the caller reports the failure and the UI uses the browser voice meanwhile.
            if _download is None or not _download.is_alive():
                _download = threading.Thread(target=_download_models, daemon=True)
                _download.start()
            raise RuntimeError("the voice model is still downloading")
        _kokoro = Kokoro(str(TTS_DIR / MODEL_FILES[0]), str(TTS_DIR / MODEL_FILES[1]))
    return _kokoro


def synthesize(text: str) -> bytes:
    """Return WAV audio of the text spoken in English."""
    voice = os.environ.get("TTS_VOICE", "").strip() or DEFAULT_VOICE
    # Questions repeat across sessions, so keep each rendered clip on disk.
    key = hashlib.sha256(f"{voice}\n{text}".encode()).hexdigest()
    cached = CACHE_DIR / f"{key}.wav"
    if cached.exists():
        return cached.read_bytes()

    # One synthesis at a time: the model is loaded once and shared.
    with _lock:
        samples, sample_rate = _get_kokoro().create(text, voice=voice, speed=1.0, lang="en-us")

    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype(np.int16)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.tobytes())
    audio = buffer.getvalue()

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(audio)
    return audio
