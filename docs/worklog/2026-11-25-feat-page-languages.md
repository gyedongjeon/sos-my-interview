---
title: "feat: show the pages in the language the user chooses"
date: 2026-11-25
branch: feat/page-languages
request-source: Claude Code session, 2026-11-25
---

## Request

When the user chooses their language under Settings, the menus and the rest of the pages should
change to that language too, as they do in the sibling app SOS My Language. Its translations were
to be used as a reference.

## Changes

- **`frontend/src/i18n/`** (new), following SOS My Language: `en.ts` has every text of the pages by
  a key; `ko.ts`, `ja.ts`, `zh-Hans.ts`, `zh-Hant.ts`, `es.ts`, `fr.ts`, `de.ts`, `pt.ts`, `it.ts`,
  `pl.ts`, `ru.ts`, `uk.ts`, `tr.ts`, `vi.ts`, `id.ts`, `th.ts`, `hi.ts`, and `bn.ts` have the same
  keys, one file for every language of `LANGUAGES` in the settings store. `index.ts` has
  - `t(key, values)`: the text in the user's language, with `{name}` filled in and `one | many`
    chosen by `n`; English for a language without a file.
  - `locale()`: the tag dates and times are written with, so "Added …" and History follow the
    user's language too (a `locale` was added to each entry of `LANGUAGES`).
  - `modelName()` and `voiceLabel()`: the speech-model names and what is said of a voice
    ("Emma · British · female" → "Emma · 영국식 · 여성"), which come from the backend in English.
- **Every page and component** uses `t()` instead of fixed English: the navigation bar, Home,
  Common questions, job postings, Résumé, History, an attempt, the interview page, Settings, the
  model downloads, and the scores. Messages made in the stores, `scores.ts`, and `useCamera.ts` are
  translated too.
- **Settings**: "Feedback language" became "Your language"; it says that the pages follow it and
  that most languages were translated by AI. Choosing a language changes the pages at once, since
  `t()` reads the store's language while a page is drawn.
- **How they were translated**: English and Korean by hand; the others by AI, from `en.ts` with
  `ko.ts` as the model and the same language files of SOS My Language for shared wording. They have
  not been checked by a native speaker. Languages with more plural forms than two (Polish, Russian,
  Ukrainian) use one wording that fits any number ("Попыток: {n}").
- **Tests**: `i18n/index.test.ts` (texts, filling in, plurals, every language has its pages, date
  tags, model and voice names) and `i18n/files.test.ts` (every language file has every key, the same
  names to fill in, no extra plural forms, and the leading ` · ` of appended texts). The settings test
  now expects its error in Korean, the user's language there.
- **Docs**: `README.md` (features, first setup, and a new "Adding a language for the pages"),
  `README.ko.md` (the Korean names of the menus and buttons in the first setup and the FAQ), and
  `AGENTS.md` (no fixed text for the user on a page).

Considered and left out:

- The question texts, the model answers, and "REC" stay in English: the app is for practising
  English interviews.
- Messages of the backend's errors stay in English, as in SOS My Language.
- Loading a language only when chosen: all are bundled, as in SOS My Language; the app is served
  from the same computer.

## Verification

- `cd frontend && npm test`: 126 passed, including the four checks of each of the 18 language files.
- `cd frontend && npm run build`: the type check passes (a file lacking a key of `en.ts` is refused).
  The script grew to about 428 kB (127 kB gzipped) with every language bundled.
- `cd backend && uv run pytest`: 108 passed (the backend is unchanged).
- Not done: looking at the pages in each language in the running app, and a reading by native speakers.
