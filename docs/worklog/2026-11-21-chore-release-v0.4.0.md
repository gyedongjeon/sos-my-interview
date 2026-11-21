---
title: "chore: release v0.4.0"
date: 2026-11-21
branch: chore/release-v0.4.0
request-source: chat session, 2026-11-21
---

## Request

Release what has been merged since `v0.3.0`. This is also the first release that an installed
app (`v0.3.0`) can update to from inside the app, so it is the first real test of that feature.

## Changes

- **Version 0.4.0** in `backend/pyproject.toml`, `frontend/package.json`, and
  `desktop/package.json`, with their lock files. MINOR is raised because the change since
  `v0.3.0` is a feature: everything the app stores is kept in one folder.

After this is merged, the merge commit is tagged `v0.4.0`, and the release workflow builds and
publishes the dmg and the zip.

## Verification

- `.github/scripts/check-version.sh v0.4.0` passes, so the tag will match the three packages.
- `uv lock --check` passes, and the backend, frontend, and desktop tests pass locally.
- Not verified here: the update from an installed `v0.3.0` to this release, which can only be
  tried once the release is published.
