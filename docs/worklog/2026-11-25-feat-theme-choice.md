---
title: "feat: choose the theme of the pages under Settings"
date: 2026-11-25
branch: feat/theme-choice
request-source: Claude Code session, 2026-11-25
---

## Request

Let the user choose the theme of the pages under Settings, as the sibling app SOS My Feed does:
an "Appearance" (화면 테마) select with System, Light, and Dark. During review in the running
app it was asked to have a card of its own, since the "Your language" card is titled for the
language only.

## Changes

- **Backend**: `GET/PUT /api/settings` has a `theme`: `""` (follow the system, the default),
  `sos` (light), or `sos-night` (dark); anything else is refused with 422. `PUT` now saves only
  the settings it is sent, so choosing the theme keeps the language and the other way round.
- **Frontend**: the settings store loads the theme and saves it with `setTheme()`; `App.vue` puts
  it on `<html data-theme>`, or removes it so daisyUI follows the system's light or dark mode
  (`prefersdark` on `sos-night`, as before). The select has a card of its own, "Appearance", between
  "Your language" and "Interviewer's voice", with one line on what it does. Its texts are in
  every language of the pages (translated by AI, except English and Korean).
- **Docs**: the first setup in `README.md` and `README.ko.md` mentions it.

Considered and left out:

- Keeping the choice in `localStorage` as well, to apply it before the settings load. The settings
  arrive from the local backend right after the page opens, as in SOS My Feed.

## Verification

- `cd backend && uv run pytest`: 111 passed (3 new in `tests/test_settings.py`).
- `cd frontend && npm test`: 130 passed (4 new store tests); `npm run build` passes.
- The built CSS applies the system's dark mode only to `:root:not([data-theme])`, so a chosen
  theme overrides it.
- Not done: switching the theme in the running app.
