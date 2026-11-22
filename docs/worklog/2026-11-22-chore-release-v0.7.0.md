---
title: "chore: release v0.7.0"
date: 2026-11-22
branch: chore/release-v0.7.0
request-source: chat session, 2026-11-22
---

## Request

Release what was merged since `v0.6.0`.

## Changes

- **Version 0.7.0** in `backend/pyproject.toml`, `frontend/package.json`, and
  `desktop/package.json`, with their lock files. MINOR is raised because there is a new feature
  since `v0.6.0`, and nothing breaks saved data or the way the app is installed:
  - The interviewer's voice can be chosen under Settings among eleven Kokoro English voices,
    American and British; British voices speak with British pronunciation (#23).
  - CI runs again on every push to a pull request (#22).

After this is merged, the merge commit is tagged `v0.7.0`. The release workflow then publishes
the dmg and the zip, and the Windows job adds the installer to the same release.

## Verification

- `.github/scripts/check-version.sh v0.7.0` passes, so the tag will match the three packages.
- `uv lock --check` passes. `cd backend && uv run pytest`: 108 passed; `cd frontend && npm test`:
  44 passed; `cd desktop && npm test`: 48 passed.
