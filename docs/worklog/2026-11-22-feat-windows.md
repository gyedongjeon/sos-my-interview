---
title: "feat: build a Windows installer"
date: 2026-11-22
branch: feat/windows
request-source: chat session, 2026-11-22
---

## Request

Make a Windows version of the app, following the Windows work already done in the sister
project `sos-my-english`.

## Changes

- **Installer for 64-bit Windows** (`electron-builder`, NSIS target): it installs for the
  current user without administrator rights and is named
  `SOS-My-Interview-Setup-<version>.exe`. It ships `uv.exe` (`desktop/scripts/fetch-uv.mjs`
  now also has the pinned Windows build and its SHA-256; the zip is unpacked with Windows'
  own `tar.exe`, since Git's `tar` takes "C:" for a remote host).
- **Python is shipped in the Windows installer** (`desktop/scripts/fetch-python.mjs`,
  `resources/python`), and the app tells uv to use it and download none. In the sister
  project's Windows trial, downloading Python from inside the app stalled every time. The
  macOS app is unchanged and still fetches its Python.
- **Stopping the backend on Windows**: uv starts the Python server as a process of its own
  there, and ending uv leaves the server running, so the whole tree is ended
  (`taskkill /T /F`, decided in `stopCommand`). The backend's console window is hidden.
- **Updates on Windows**: only the macOS app can replace itself. On Windows the app reports a
  new version and opens the download page; the check is under Help in a small menu.
- **The first launch shows a progress bar** and the step in words ("Downloading packages…
  120 of 450 MB", "Installing packages…", "Starting…"), read from uv's output
  (`startupProgress`). The packaged app keeps the backend's output in `backend.log`.
- **Database connections are closed after use** (`get_connection()` is now a context manager
  that commits or rolls back and then closes). An open connection keeps the database file
  locked on Windows; the tests' cleanup no longer ignores a folder it cannot remove.
- **Camera and microphone failures say why** (`deviceProblem`): no device, access turned off
  in the system's privacy settings, the device held by another app, or the failure's name.
  When the system refuses a device, the app offers to open that page of the system settings
  (Windows never asks a desktop app). The camera is offered at most once per launch, since
  it is optional.
- **Release workflow**: a Windows job builds the installer after the release exists and adds
  it to the release; the release notes have a Windows section.
- **CI**: a Windows job runs the backend's tests, starts the server the way the installed app
  does on the shipped Python (`.github/scripts/start-server-check.sh`), builds the installer,
  checks that it holds the backend, uv, and Python, and keeps it as an artifact for 7 days.
- `README.md` and `README.ko.md`: Windows install, update, and uninstall steps.
- Not included: an installer for Intel Macs or Linux, signing the Windows installer, and the
  desktop unit tests on Windows.

## Verification

- `cd backend && uv run pytest`: 99 passed, 3 live tests deselected.
- `cd frontend && npm test`: 41 passed; `npm run build` succeeded.
- `cd desktop && npm test`: 47 passed; `npx tsc --noEmit` succeeded.
- `.github/scripts/start-server-check.sh` on macOS: the server started and answered
  `/api/health` and `/api/questions`, and was stopped afterwards.
- **Not verified yet: anything on Windows.** The Windows CI job runs when this pull request is
  opened. Nobody has opened the installed app on a Windows machine: the installer, the first
  launch and its progress bar, the camera and microphone, the settings dialog, closing the
  app (that the server stops), the update notice, and uninstalling are all unchecked.
