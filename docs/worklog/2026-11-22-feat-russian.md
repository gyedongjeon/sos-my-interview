---
title: "feat: add Russian as a feedback language"
date: 2026-11-22
branch: feat/russian
request-source: chat session, 2026-11-22
---

## Request

Offer Russian as a language the written feedback is in, so the series website (`sos-my-app`,
served at sosmy.app) can add a Russian page whose promise of "feedback in your language" is
true. The same change is made in `sos-my-english`.

## Changes

- `frontend/src/stores/settings.ts`: Russian (`Русский`, browser code `ru`) added to
  `LANGUAGES`, after Portuguese. It appears in the Settings menu, and a first launch in a
  Russian-language browser starts from it.
- Nothing else needed changing: the backend takes the language as free text and passes it to
  the model (`feedback_language()`), and no data is kept per language.
- A test case for `ru-RU -> Russian` was added first and seen to fail (`expected 'English' to be
  'Russian'`) before the list was changed.

## Verification

- `cd frontend && npm test`: 31 passed; `npm run build` succeeded.
- `cd desktop && npm test`: 30 passed; `npx tsc --noEmit` succeeded.
- `cd backend && uv run pytest`: 97 passed, 3 live tests deselected.
- With the Gemini key in `backend/.env`, ran a temporary copy of
  `test_feedback_follows_the_schema_and_the_chosen_language` with "Russian" and a Cyrillic check
  instead of Korean: passed, so real feedback summaries were written in Russian and the better
  answer stayed in English. The temporary test was deleted and is not committed.
- Not verified: the Settings menu in the running app, and a release; installed apps get Russian
  with the next version.
