---
title: Run CI again on every push to a pull request
date: 2026-11-22
branch: chore/ci-run-on-every-push
request-source: Claude Code chat, 2026-11-22
---

## Request

CI ran only when a pull request was opened (or reopened), so later commits pushed to the pull request were never tested. Make it run on those pushes too, following the CI workflow of the sibling `sos-my-german` project.

## Changes

- `.github/workflows/ci.yml`: added `synchronize` to the `pull_request` trigger types, so every push to an open pull request into `main` runs the checks again. The existing `concurrency` group (`cancel-in-progress: true`) cancels the run still going for the previous push, so rapid pushes do not pile up runs. Updated the header comment to match. The file is now identical to the `sos-my-german` one.
- `AGENTS.md`: replaced the note that CI does not run again on later pushes with the new behavior.

## Verification

- `diff` against `sos-my-german/.github/workflows/ci.yml`: no differences.
- Searched the Markdown docs for other mentions of the old trigger; only `AGENTS.md` had one.
