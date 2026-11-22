---
title: "perf: start the app in under a second instead of four"
date: 2026-11-22
branch: perf/faster-startup
request-source: chat session, 2026-11-22
---

## Request

On both Windows and macOS, opening the app again after quitting it stayed on "Starting…" for a
long time. Make it start faster, the same way as the sister project `sos-my-english`.

## Changes

These commits were made on `feat/windows` after its pull request (#19) had been merged, so they
come in this pull request instead.

- **No compiled files were kept.** The desktop app ran the backend with
  `PYTHONDONTWRITEBYTECODE=1` to keep compiled files out of the app bundle, which also kept them
  out of the package folder: the installed macOS app's `venv` held 8,020 `.py` files and no
  `.pyc`, so every launch compiled them again. `desktop/src/backend.ts` now sets
  `PYTHONPYCACHEPREFIX` to `<userData>/pycache` for the packaged app instead, so compiled files
  are kept there and the bundle stays unchanged. A checkout keeps `PYTHONDONTWRITEBYTECODE`.
  The CI server check starts the server like the packaged app.
- **LiteLLM took about 1.8 s of the 2.5 s it took to load the backend**, and downloaded its
  model price list on every start. `app/llm.py` now uses the price list LiteLLM ships with
  (`LITELLM_LOCAL_MODEL_COST_MAP=True`; prices are not used here) and loads LiteLLM on first use
  (`load()`). The server starts a background thread to load it once it is up, so a request that
  needs it sooner waits for it. No other module imports LiteLLM.
- `README.md`: `pycache/` added to the list of what the app keeps in its folder.

## Verification

- New tests, each seen to fail first: `desktop/tests/backend.test.ts` (compiled files go to
  `<userData>/pycache` for the packaged app; a checkout keeps `PYTHONDONTWRITEBYTECODE`) and
  `backend/tests/test_startup.py` (in a fresh interpreter: the server loads without LiteLLM,
  LiteLLM is loaded in the background after startup, and the shipped price list is used).
- `cd backend && uv run pytest`: 102 passed. `uv run --env-file .env pytest -m live`: 3 passed,
  so real model calls still work with LiteLLM loaded later.
- `cd desktop && npm test`: 48 passed; `npx tsc --noEmit` succeeded. `cd frontend && npm test`:
  41 passed.
- Time on macOS (M-series) until `/api/health` answers, from a fresh `venv` of the locked
  packages: 3.9 s with only compiled files kept; with both changes 2.1 s on the first start and
  0.83 to 0.9 s after. Loading the backend without any kept compiled files took about 7.8 s.
- CI on `feat/windows` with the same code passed on Windows (backend tests, server start,
  installer built). The installed app on Windows has been tried but the later-launch time
  there has not been measured yet; installed apps get this with the next release.
