"""The models the app downloads on first use, and their download progress."""

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from . import speech, transcribe

router = APIRouter(prefix="/api")


class ModelStatus(BaseModel):
    id: str
    label: str
    state: Literal["missing", "downloading", "ready", "error"]
    # Bytes on disk so far, and the expected size when it is known.
    downloaded: int
    total: int | None
    error: str | None


def _statuses() -> list[ModelStatus]:
    return [ModelStatus(**download.status()) for download in (transcribe.model_download, speech.model_download)]


@router.get("/models", response_model=list[ModelStatus])
def list_models() -> list[ModelStatus]:
    return _statuses()


@router.post("/models/download", response_model=list[ModelStatus])
def download_models() -> list[ModelStatus]:
    """Start downloading whatever is missing. The page calls this when it opens, so the models
    are usually there before the first answer needs them."""
    transcribe.model_download.start()
    speech.model_download.start()
    return _statuses()
