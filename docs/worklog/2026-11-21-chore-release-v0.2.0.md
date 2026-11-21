---
title: "chore: release v0.2.0"
date: 2026-11-21
branch: chore/release-v0.2.0
request-source: chat session, 2026-11-21
---

## Request

Release what has been merged since `v0.1.0`, so that the downloadable installer matches the
README: `main` bundles uv, but the `v0.1.0` installer still needs uv installed.

## Changes

- **Version 0.2.0** in `backend/pyproject.toml`, `frontend/package.json`, and
  `desktop/package.json`, with their lock files. MINOR is raised because the changes since
  `v0.1.0` include a feature (uv bundled in the desktop app) and nothing breaking; the others
  are the release workflow, the desktop tests, and the README work.
- **READMEs**: the sentence saying that `v0.1.0` needs uv installed first is removed from
  `README.md` and `README.ko.md`, since the latest release will no longer need it.

After this is merged, the merge commit is tagged `v0.2.0`. Pushing the tag is the first run of
the release workflow, which builds the dmg and publishes the GitHub Release.

## Verification

- `.github/scripts/check-version.sh v0.2.0` passes, so the tag will match the three packages.
- `uv lock --check` passes, and the backend, frontend, and desktop tests pass locally.
- Not verified: the release workflow itself, which has never run. Its result is checked after
  the tag is pushed; if it fails, the fix goes to `main` and is released as a new version.
