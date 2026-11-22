---
title: "chore: release v0.6.0"
date: 2026-11-22
branch: chore/release-v0.6.0
request-source: chat session, 2026-11-22
---

## Request

Release what was merged since `v0.5.1`, including the first Windows installer.

## Changes

- **Version 0.6.0** in `backend/pyproject.toml`, `frontend/package.json`, and
  `desktop/package.json`, with their lock files. MINOR is raised because there are new
  features since `v0.5.1`, and nothing breaks saved data or the way the app is installed:
  - Feedback in Russian, Turkish, Italian, Thai, Polish, Ukrainian, and Bengali (#17, #18).
  - A Windows installer for 64-bit Windows, built by the release workflow (#19).
  - The first launch shows a progress bar; camera and microphone errors say why, and the app
    offers the system's privacy settings when access is turned off (#19).
  - Later launches start in under a second instead of several seconds (#20).
  - Database connections are closed after use (#19).
- `docs/git-workflow/versioning.md`: the release steps mention the Windows installer that the
  release workflow adds.

After this is merged, the merge commit is tagged `v0.6.0`. The release workflow then publishes
the dmg and the zip, and the Windows job adds the installer to the same release.

## Verification

- `.github/scripts/check-version.sh v0.6.0` passes, so the tag will match the three packages.
- `uv lock --check` passes. `cd backend && uv run pytest`: 102 passed; `cd frontend && npm test`:
  41 passed; `cd desktop && npm test`: 48 passed.
- This is the first release with the Windows job in `release.yml`. The same build steps passed
  in CI on #19 and #20, and an installer from that CI was tried on a Windows machine; the job
  that uploads to a release has not run before.
