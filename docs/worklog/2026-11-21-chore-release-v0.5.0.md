---
title: "chore: release v0.5.0"
date: 2026-11-21
branch: chore/release-v0.5.0
request-source: chat session, 2026-11-21
---

## Request

Release what has been merged since `v0.4.0` now, rather than holding it until Windows support,
which is a larger piece of work with its own release.

## Changes

- **Version 0.5.0** in `backend/pyproject.toml`, `frontend/package.json`, and
  `desktop/package.json`, with their lock files. MINOR is raised because the changes since
  `v0.4.0` include a feature: the speech models are downloaded when the app opens, with their
  progress shown. Also included is a fix: failed LLM requests are retried and report their real
  cause, instead of "tenacity import failed".

After this is merged, the merge commit is tagged `v0.5.0`, and the release workflow builds and
publishes the dmg and the zip.

## Verification

- `.github/scripts/check-version.sh v0.5.0` passes, so the tag will match the three packages.
- `uv lock --check` passes, and the backend, frontend, and desktop tests pass locally.
- Not verified here: the update from an installed `v0.4.0` to this release, and the download
  banner inside the desktop app, which can be looked at after updating.
