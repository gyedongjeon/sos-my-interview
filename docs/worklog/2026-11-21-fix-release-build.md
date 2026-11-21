---
title: "fix: let the release workflow build the dmg"
date: 2026-11-21
branch: fix/release-build
request-source: release workflow run for v0.2.0, 2026-11-21
---

## Request

The first run of the release workflow, for the `v0.2.0` tag, failed in "Build the installer",
so no release was published. Fix it and release again.

## Changes

- **Cause**: with a GitHub token in the environment of a CI build, electron-builder looks for a
  place to publish to, even with `--publish never`, in order to write update information. It
  could not work out the repository from `desktop/` and crashed with `Cannot read properties of
  null (reading 'provider')` after the dmg itself had been built.
- **Fix**: `"publish": null` in the electron-builder configuration turns that off; the release
  is created with `gh` as before. The token is also no longer in the environment of the build
  step, only of the step that publishes.
- **Version 0.2.1**: the `v0.2.0` tag stays as it is, without a release, because tags are never
  moved or reused. The same content plus this fix is released as `v0.2.1`. The three packages
  and their lock files are raised in a separate `chore: release v0.2.1` commit.

## Verification

- The failure was reproduced locally by running electron-builder with `CI`, `GITHUB_ACTIONS`,
  and a dummy `GH_TOKEN` set: same error, after the dmg was built.
- With `"publish": null`, the same command under the same variables finishes without the error
  and produces the dmg.
- `check-version.sh v0.2.1` passes; the backend, frontend, and desktop tests pass locally.
- Not verified: a complete run of the release workflow. The steps after the build (release
  notes, publishing) have still never run; they first run when `v0.2.1` is tagged.
