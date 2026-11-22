---
title: "feat: choose the interviewer's voice under Settings"
date: 2026-11-22
branch: feat/voice-choice
request-source: chat session, 2026-11-22
---

## Request

Let the user choose the interviewer's text-to-speech voice, the same way the sibling app
SOS My English recently added it.

## Changes

- **Voices**: the same eleven Kokoro English voices as SOS My English, American and British,
  female and male: Heart (the default, as before), Bella, Nicole, Sarah, Michael, Fenrir, Puck,
  Emma, Isabella, George, and Fable.
- **No download**: Kokoro keeps every voice in the one `voices-v1.0.bin` already downloaded, so
  choosing a voice downloads nothing; the download code is unchanged.
- **Accent**: a British voice (prefix `b`) is now spoken with `lang="en-gb"`, the others with
  `en-us` as before.
- **Backend**: `speech.VOICES` lists them. `GET /api/voices` returns each with which one is
  chosen; `PUT /api/voice` keeps the choice in the `settings` table (422 for an unlisted voice).
  The voice in use is the choice, else `TTS_VOICE`, else `af_heart`. The clip cache was already
  keyed by voice.
- **Frontend**: an "Interviewer's voice" card on the Settings page with the voices and "Hear it"
  to play an interview-style sample line.
- **Docs**: the README describes the choice; the Korean README adds it to the first setup;
  `.env.example` notes that the Settings choice comes before `TTS_VOICE`.

## Verification

- `cd backend && uv run pytest`: 108 passed (6 new in `tests/test_voice_choice.py`).
- `cd frontend && npm test`: 44 passed (3 new store tests); `npm run build` succeeded.
- Against a temporary data folder with the real Kokoro model: `GET /api/voices` listed the
  voices with Heart chosen, `PUT /api/voice` with `bm_george` chose it, an unknown voice returned
  422, and synthesis returned WAV audio.
- Not verified: the Settings card in a browser, and listening to the voices in the app.
