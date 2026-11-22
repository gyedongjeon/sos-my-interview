---
title: "feat: add six more feedback languages"
date: 2026-11-22
branch: feat/more-languages
request-source: chat session, 2026-11-22
---

## Request

Offer Turkish, Italian, Thai, Polish, Ukrainian, and Bengali as languages the written feedback
is in.

## Changes

- `frontend/src/stores/settings.ts`: added to `LANGUAGES`, grouped with nearby languages:
  Italian (`Italiano`, `it`), Polish (`Polski`, `pl`), Ukrainian (`Українська`, `uk`), and
  Turkish (`Türkçe`, `tr`) among the European ones; Thai (`ไทย`, `th`) and Bengali (`বাংলা`,
  `bn`) among the Asian ones. They appear in the Settings menu, and a first launch in a browser
  set to one of them starts from it.
- Nothing else needed changing: the backend takes the language as free text and passes it to
  the model, and no data is kept per language.
- Test cases for `tr-TR`, `it-IT`, `th-TH`, `pl-PL`, `uk-UA`, and `bn-BD` were added first and
  seen to fail (`expected 'English' to be 'Turkish'`, ...) before the list was changed.

## Verification

- `cd frontend && npm test`: 37 passed; `npm run build` succeeded.
- `cd desktop && npm test`: 30 passed; `npx tsc --noEmit` succeeded.
- `cd backend && uv run pytest`: 97 passed, 3 live tests deselected.
- Not verified: live LLM feedback in the new languages, the Settings menu in the running app,
  and a release; installed apps get the new languages with the next version.
