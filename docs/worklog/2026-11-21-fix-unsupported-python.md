---
title: "fix: pin the Python the app installs"
date: 2026-11-21
branch: fix/unsupported-python
request-source: chat report of a failed first launch of the packaged app, 2026-11-21
---

## Request

The packaged app stopped on its first launch with "The interview server stopped", exit code 2.
uv had downloaded CPython 3.15.2 and then could not install `onnxruntime` 1.32.0, which has
wheels for Python 3.12 to 3.14 only. Fix the launch, and pin the Python version rather than
only excluding the broken one.

## Changes

- **Cause**: `requires-python` was `>=3.12` with no upper bound and nothing named a Python
  version, so the uv shipped with the app installed the newest Python it knew. Once that became
  3.15, the locked `onnxruntime` had no wheel for it and no source distribution to build from.
- **Pin**: `backend/.python-version` now says `3.14`, and the packaged app ships that file next
  to `pyproject.toml` and `uv.lock`. Development, CI, and the packaged app therefore all use the
  same Python minor version. The patch version is left open: wheels work across patch versions,
  and an exact patch would have to be known to every uv in use, including older installed ones.
- **Upper bound**: `requires-python` is now `>=3.12,<3.15`, and `uv.lock` was resolved again for
  that range. No package version changed; the lock only lost its Python 3.15 entries.
- **Existing installs**: a launch that already failed left a Python 3.15 environment in the
  app's folder. uv replaces an environment whose Python does not match, so nothing has to be
  removed by hand.
- **Tests**: a backend test reads `uv.lock` and fails when a package without a source
  distribution has no wheel for a Python that `requires-python` allows; another checks that the
  pinned version is inside that range. A desktop test checks that the pin is among the files
  the packaged app ships.
- Considered and rejected: passing `--python` from the desktop launcher. It would pin the
  packaged app only, leaving development and CI free to use a different Python.

## Verification

- The new backend test failed before the change (`onnxruntime` on Python 3.15 among the
  missing wheels) and passes after it. The pin tests failed before the pin was added.
- `uv run pytest` in `backend/`: 97 passed, now on Python 3.14. `npm test` and
  `npx tsc --noEmit` in `desktop/` pass.
- First launch simulated with the uv shipped in the app (0.13.9): only the files the app ships
  were copied to an empty folder, an environment with Python 3.15.2 was put in place as the
  failed launch leaves it, and uv was limited to the Pythons it installs itself. `uv run
  --frozen --no-dev` replaced the environment with Python 3.14.10, installed the 94 packages,
  and imported `onnxruntime`, `faster_whisper`, `kokoro_onnx`, and `app.main`.
- Not verified: a rebuilt installer opened from Finder. The frontend tests were not run; no
  frontend file changed.
