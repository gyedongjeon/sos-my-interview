---
title: "chore: release v0.8.0"
date: 2026-11-25
branch: chore/release-v0.8.0
request-source: Claude Code session, 2026-11-25
---

## Request

Release what was merged since `v0.7.0`.

## Changes

- **Version 0.8.0** in `backend/pyproject.toml`, `frontend/package.json`, and
  `desktop/package.json`, with their lock files. MINOR is raised because there are new features
  since `v0.7.0`, and nothing breaks saved data or the way the app is installed:
  - The pages are shown in the language chosen under Settings, in every one of the 19 languages
    offered; all but English and Korean are AI translations (#25).
  - The theme can be chosen under Settings: follow the system, light, or dark (#26).
  - The English level (CEFR A2 to C1) can be chosen under Settings; better answers and corrected
    sentences are written at it or one step above, and questions are worded for it. Scores do
    not depend on it (#27).

After this is merged, the merge commit is tagged `v0.8.0`. The release workflow then publishes
the dmg and the zip, and the Windows job adds the installer to the same release.

## Verification

- `.github/scripts/check-version.sh v0.8.0` passes, so the tag will match the three packages.
- `uv lock --check` passes. `cd backend && uv run pytest`: 121 passed; `cd frontend && npm test`:
  134 passed; `cd desktop && npm test`: 48 passed.
