---
title: "feat: keep everything the app stores in one folder"
date: 2026-11-21
branch: feat/app-data-folder
request-source: chat session, 2026-11-21
---

## Request

Deleting the app left large files in shared folders of the home folder: the Whisper model in
Hugging Face's cache and uv's download cache. Keep them with the app's other files, so that
removing one folder removes everything, and tell users how to uninstall completely.

## Changes

- **Whisper model**: downloaded into `whisper/` in the data folder (next to the database and the
  voice model) instead of `~/.cache/huggingface/`. This applies to a checkout too
  (`backend/data/whisper/`).
- **uv's downloads**: the packaged app now points uv's cache and the Python it installs at its
  own folder (`uv-cache/` and `python/` beside `venv/` and `data/`), instead of `~/.cache/uv`
  and `~/.local/share/uv/python`. A checkout keeps using the developer's own uv folders.
- **Launch code**: the uv arguments and environment moved from `main.ts` into
  `desktop/src/backend.ts` as a function of its inputs, in a separate `refactor` commit with
  tests of the existing behavior, before the new variables were added.
- **Docs**: both READMEs list what is in `~/Library/Application Support/SOS My Interview/` and
  say that uninstalling completely means deleting that folder after the app, and which shared
  cache folders earlier versions may have left.

Effects on existing users: the Whisper model is downloaded once more (about 480 MB) into the new
place, and the copies in the shared caches are not removed automatically, because other tools
may use those folders.

Considered and not done: running uv without a cache, which would avoid keeping the downloaded
packages twice on disk listings but would download every package again whenever the
dependencies change.

## Verification

- The tests for the model folder (backend) and for uv's folders (desktop) were written first and
  failed; the backend (80), frontend (21), and desktop (29) tests pass, and `tsc` passes.
- With a temporary data folder, loading a small Whisper model and transcribing a second of
  silence downloaded the model into `<data>/whisper/`, and nothing was added to
  `~/.cache/huggingface/hub`.
- A packaged build was launched after removing the app's Python environment: uv created
  `venv/` and `uv-cache/` inside the app's folder and the backend answered. `du` reports about
  458 MB for each; on APFS uv links the two rather than copying, which `du` does not show, so
  the real extra space was not measured.
- Not verified: `python/`, since this machine has a suitable Python and uv did not need to
  install one, and the full 480 MB default model in the new place.
