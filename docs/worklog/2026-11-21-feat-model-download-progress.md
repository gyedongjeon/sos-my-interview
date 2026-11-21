---
title: "feat: download the speech models up front and show progress"
date: 2026-11-21
branch: feat/model-download-progress
request-source: chat session, 2026-11-21
---

## Request

In the installed app the first answer sat on "Transcribing your answer…" for minutes with no
explanation, because the speech recognition model (about 480 MB) was being downloaded inside
that request. Show what is happening.

## Changes

- **Downloads start when the app opens**: the page asks the backend to download whatever is
  missing (the Whisper model and the Kokoro voice) in the background, so they are usually there
  before the first answer. Nothing is downloaded by merely starting the server.
- **Progress is shown**: a banner under the navigation bar lists each model with a progress bar,
  percentage, and megabytes, and disappears when both are done. A failed download is shown with
  its error and a "Try again" button.
- **The first answer explains its wait**: if an answer is given before the speech recognition
  model is there, the interview page says that the model is downloading, with the percentage,
  instead of only "Transcribing your answer…". The answer is transcribed when it finishes, as
  before.
- **Backend**: `app/downloads.py` has one small class for a background download with a state
  (`missing`, `downloading`, `ready`, `error`); both models use it. `GET /api/models` reports
  the states and `POST /api/models/download` starts what is missing. Progress is measured from
  the bytes on disk, partial files included. The total size of the Whisper model is asked from
  Hugging Face; the voice files are a pinned release with a known size.
- **Plain Hugging Face downloads**: the library's default (Xet) transfer collected the large
  file in a cache of its own under `~/.cache/huggingface`, outside the app's folder, where its
  progress could not be seen. `HF_HUB_DISABLE_XET` is now set, so the file is written straight
  into the data folder.
- **A freeze found while testing**: checking whether the Whisper model is complete waits for a
  running download of it. The state of a running download is therefore reported without that
  check; otherwise the progress request itself hung until the download ended.

## Verification

- Tests were written first for each part: the download class, the endpoints, the Xet setting,
  the status during a download, and the page's store (polling until done, stopping afterwards,
  surviving a failed request). Backend 95, frontend 30, and desktop 29 tests pass, and the
  frontend builds.
- A server on an empty data folder: opening the page started both downloads, and a screenshot
  shows the banner with both progress bars.
- The real default Whisper model was downloaded through the new code twice. The run after the
  freeze was fixed reported 3 MB, 204 MB, then ready at 486 MB over 30 seconds, with each
  status request answering at once, and the model ended up in the data folder. Earlier runs
  were slow or looked stuck at 3 MB because of a network problem at the time.
- Not verified: the interview page's waiting message and the error banner on screen, the
  download banner inside the desktop app, and what the page shows when a download stalls
  without failing (it keeps showing the last progress).
