---
title: "docs: restructure the README and add a Korean README"
date: 2026-11-21
branch: docs/readme
request-source: chat session, 2026-11-21
---

## Request

Improve the README, and add a Korean one. The app is for people who are not native English
speakers, and the steps where they get stuck (the unsigned-app warning, the API key) are the
ones worth reading in their own language.

## Changes

- **`README.md` restructured for users first**: it used to open with one line and the commands
  for a development server. It now opens with what the app does, badges (release, CI, license),
  a screenshot, and a feature list, followed by installing from a release, first setup, and how
  each part works. Running from source, tests, and the project structure come after. No
  information was dropped; the tech stack moved from the overview to the structure section.
- **`README.ko.md` added**: a shorter Korean README for users with the introduction, features,
  installing, first setup, a walk through one interview, and common questions (the macOS
  warning, the slow first launch, model downloads). Development topics link to the English
  README instead of being translated, so that only the parts users need exist twice.
- **Language rule**: `AGENTS.md` keeps "documentation in English" and names `README.ko.md` as the
  one exception, to be updated in the same PR whenever the matching parts of `README.md` change.
- **Screenshot**: `docs/images/home.png`, taken from a server with an empty data folder.
- Both READMEs say that only `v0.1.0` needs uv installed first: `main` already bundles uv, but
  the latest released installer does not until the next release.

## Verification

- The button and section names quoted in the Korean walk-through were each found in the
  frontend source.
- The screenshot was taken from the current build and looked at.
- Relative links (`README.ko.md`, `LICENSE`, `docs/images/home.png`, the notices file, the
  versioning document) point to files that exist.
- Not verified: how the badges and the screenshot render on GitHub (visible once pushed); the
  statement that the system voice reads questions while the voice model downloads describes the
  intended fallback, which has not been heard in a browser or in the desktop app; and the
  Gemini free tier is as known at the time of writing.
