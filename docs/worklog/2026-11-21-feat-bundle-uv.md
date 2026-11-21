---
title: "feat: bundle uv in the desktop app"
date: 2026-11-21
branch: feat/bundle-uv
request-source: chat session, 2026-11-21
---

## Request

Let people install the desktop app without installing uv first. Of the options discussed, the
one chosen was to ship the uv program inside the app.

## Changes

- **uv ships inside the app**: the packaged app now contains uv at `Resources/uv/uv` and uses
  it before any installed one, so a user only needs the dmg. uv also downloads Python itself
  when the machine has no suitable one. The first launch still downloads the Python packages
  (about 455 MB installed), so it needs a network connection and takes a few minutes.
- **Pinned download at build time**: `npm run dist` and `npm run package` first run
  `desktop/scripts/fetch-uv.mjs`, which downloads uv 0.13.9 for Apple Silicon from uv's GitHub
  releases into `desktop/vendor/` (git-ignored), and refuses to unpack it unless its SHA-256 is
  the pinned one. The binary is not committed. Building for another platform needs an entry
  for it in that script.
- **Lookup moved and tested**: the uv lookup moved from `main.ts` into `desktop/src/uv.ts` as a
  function of its inputs (a separate `refactor` commit), and the desktop package got its first
  tests (Vitest, 6). The pull request workflow now runs them.
- **Running from a checkout is unchanged**: development still uses the developer's own uv.
- **Notices and docs**: uv (MIT or Apache-2.0, used under MIT) is added to the third-party
  notices and the Settings list. The README and the release notes no longer tell users to
  install uv.
- The installer grows from about 120 MB to about 134 MB.

Alternatives not taken: bundling a whole Python environment (a 600 MB+ installer and signing
trouble) and freezing the backend with PyInstaller (fragile with Whisper and ONNX Runtime, as
noted when the desktop app was first built). Both would also remove the first-launch download.

## Verification

- The new lookup tests were written first and failed (2 of 6) before the change; all 6 pass
  after it. `tsc` passes in `desktop/`.
- `npm run uv` downloaded uv 0.13.9, and a second run found it already in place.
- `npm run dist` built the dmg with `Resources/uv/uv` inside, executable and ad-hoc signed;
  `codesign --verify --deep` passes on the app.
- The packaged app was launched after deleting its Python environment: the process list showed
  the backend started by the bundled uv, the environment was recreated by uv 0.13.9 from the
  lock file written by uv 0.11.3, without the test tools, and `/api/health` answered after
  about 90 seconds. Quitting stopped the backend.
- The bundled uv, told to ignore installed Pythons, downloaded Python 3.12 by itself and
  created an environment with it.
- Not verified: installing the downloaded dmg on a Mac that has neither uv nor Python (the
  machine used has both), and the changed desktop job of the workflow, which first runs when
  the pull request is opened.
