"""Speech-to-text setup: which model is loaded and where it is kept."""

import pytest

from app import transcribe
from app.paths import DATA_DIR


class FakeWhisperModel:
    """Stands in for the Whisper model and records how it was loaded."""

    loads: list[dict] = []

    def __init__(self, name, **options):
        FakeWhisperModel.loads.append({"name": name, **options})


@pytest.fixture(autouse=True)
def fake_model(monkeypatch):
    FakeWhisperModel.loads = []
    monkeypatch.setattr(transcribe, "WhisperModel", FakeWhisperModel)
    monkeypatch.setattr(transcribe, "_model", None)
    monkeypatch.delenv("WHISPER_MODEL", raising=False)


def test_model_is_kept_in_the_app_data_folder():
    transcribe._get_model()
    # Next to the database and the voice model, so removing one folder removes it too.
    assert FakeWhisperModel.loads[0]["download_root"] == str(DATA_DIR / "whisper")


def test_default_model_is_the_small_english_one():
    transcribe._get_model()
    assert FakeWhisperModel.loads[0]["name"] == "small.en"


def test_another_model_can_be_chosen_with_the_environment(monkeypatch):
    monkeypatch.setenv("WHISPER_MODEL", " medium.en ")
    transcribe._get_model()
    assert FakeWhisperModel.loads[0]["name"] == "medium.en"


def test_model_is_loaded_once():
    assert transcribe._get_model() is transcribe._get_model()
    assert len(FakeWhisperModel.loads) == 1
