---
title: "feat: fit better sentences to the user's English level"
date: 2026-11-25
branch: feat/english-level
request-source: Claude Code session, 2026-11-25
---

## Request

Let the user set their English level on the European (CEFR) scale, such as A2, B1, or B2, so
that the sentences the app recommends fit their level. Of the two ways discussed, having the
user choose the level and estimating it from their answers, the user chooses it for now;
showing an estimate as a hint may follow later.

## Changes

- **Setting**: `GET/PUT /api/settings` has an `english_level`: `""` (not chosen, the default),
  `A2`, `B1`, `B2`, or `C1`; anything else is refused with 422. A1 and C2 are left out: A1 is too
  early for interview practice, and C2 needs no fitting.
- **Prompts** (`backend/app/levels.py`): with a level, the model is told
  - for feedback, to write `better_answer` and every corrected sentence at the level or at most
    one step above (C1 stays at C1), so the user can learn them and say them aloud, preferring
    simpler correct constructions;
  - for follow-up and tailored questions, to word them so the user understands them by ear,
    without changing what is asked or how demanding it is (the existing difficulty choice keeps
    that).
  Without a level the prompts are as before.
- **Scores do not depend on the level**, and the prompt says so, so scores in History stay
  comparable over time.
- **Frontend**: an "English level" card on the Settings page, between "Your language" and
  "Appearance", with one line for each level (e.g. "B1 · explain your experience and reasons on
  familiar topics"). Its texts are in every language of the pages (AI translations, except English
  and Korean).
- **Docs**: `README.md` (features and Feedback) and `README.ko.md` (features and first setup).

Considered and left out:

- Estimating the level from the answers. Answers are short, spoken under pressure, and pass
  through speech recognition, so an estimate would be noisy and would make the better sentences
  change level from one attempt to the next. It may come later as a hint the user can accept.
- The speaking (pronunciation) feedback is not fitted: its tips name words from the answer.

## Verification

- `cd backend && uv run pytest`: 121 passed (10 new: the setting, and what the feedback,
  follow-up, and tailored-question prompts are told with and without a level).
- `cd frontend && npm test`: 134 passed (4 new store tests); `npm run build` passes.
- Not done: a live run comparing the better answer at different levels.
