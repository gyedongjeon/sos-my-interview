---
title: "chore: release v0.5.1"
date: 2026-11-21
branch: chore/release-v0.5.1
request-source: chat session, 2026-11-21
---

## Request

Release the fix for the failed first launch right away, so that a new install of the app works
again.

## Changes

- **Version 0.5.1** in `backend/pyproject.toml`, `frontend/package.json`, and
  `desktop/package.json`, with their lock files. PATCH is raised because the only change since
  `v0.5.0` is a fix: the Python the app installs is pinned to 3.14. Without the pin, uv
  installed Python 3.15, for which a required package has no build, and the server never
  started.

After this is merged, the merge commit is tagged `v0.5.1`, and the release workflow builds and
publishes the dmg and the zip.

## Verification

- `.github/scripts/check-version.sh v0.5.1` passes, so the tag will match the three packages.
- `uv lock --check` passes, and the backend, frontend, and desktop tests pass locally.
- Not verified here: the first launch of the installer this release builds. The fix itself was
  checked with the uv the app ships, against only the files the app ships.
