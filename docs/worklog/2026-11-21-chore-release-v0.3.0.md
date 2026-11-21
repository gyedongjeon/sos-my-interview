---
title: "chore: release v0.3.0"
date: 2026-11-21
branch: chore/release-v0.3.0
request-source: chat session, 2026-11-21
---

## Request

Release what has been merged since `v0.2.1`, so that people who install the app from now on can
update it from inside the app.

## Changes

- **Version 0.3.0** in `backend/pyproject.toml`, `frontend/package.json`, and
  `desktop/package.json`, with their lock files. MINOR is raised because both changes since
  `v0.2.1` are features: the app icon and updating from inside the app.

After this is merged, the merge commit is tagged `v0.3.0`, and the release workflow builds and
publishes the dmg and, for the first time, the zip that installed apps update from.

## Verification

- `.github/scripts/check-version.sh v0.3.0` passes, so the tag will match the three packages.
- `uv lock --check` passes, and the backend, frontend, and desktop tests pass locally.
- Not verified here: the release workflow's upload of the zip, which first happens for this
  tag, and an update between two published releases, which needs the release after this one.
