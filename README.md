# sos-my-interview

A web-based mock interview service for personal use.

## Overview
- **Frontend**: Video-call style web UI that reads questions aloud, records your answer from the webcam, and shows scored feedback and history — Vue 3, TypeScript, Vite, Vue Router, Pinia, Tailwind CSS + daisyUI.
- **Backend**: API server that serves questions, transcribes answers (Whisper) and reads questions aloud (Kokoro) locally, and uses an LLM for tailored questions, follow-up questions, and scored feedback — FastAPI (Python).
- **Database**: SQLite (local, single-user).

The service is intended to run locally; no deployment or multi-user support is planned for now.

## Getting Started
Run the backend and frontend in separate terminals, then open http://localhost:5173.

```bash
# Backend (http://127.0.0.1:8000)
cd backend
uv run uvicorn app.main:app --reload

# Frontend (http://localhost:5173)
cd frontend
npm install
npm run dev
```

### Desktop app
The same app also runs in its own window (Electron), with the backend started and stopped for
you. An installer for Apple Silicon Macs is attached to each
[release](https://github.com/gyedongjeon/sos-my-interview/releases), with install steps in the release
notes; it needs [uv](https://docs.astral.sh/uv/) installed.

To run or build it from this checkout, you need uv and Node.js:

```bash
cd desktop
npm install
npm run dev    # run from this checkout, using backend/data
npm run dist   # build desktop/release/SOS My Interview-<version>-arm64.dmg
```

The built app installs its Python dependencies on the first launch (this can take a few
minutes) and keeps its own data, separate from this checkout, in
`~/Library/Application Support/SOS My Interview/data/`. The
build is not signed with a developer certificate, so it is meant for the machine that built it.

### AI model and API key
Tailored questions, follow-up questions, and feedback are written by an LLM through
[LiteLLM](https://docs.litellm.ai/docs/providers), so any supported provider works (Gemini,
Claude, OpenAI, OpenRouter, a local Ollama model, ...). The app opens on the Settings page the
first time: choose a provider and model, paste that provider's API key, and it is saved and
checked with a test request. Change it any time under Settings. The key is stored in the local
database (`app.db`), is never shown again in the UI, and is sent only to the chosen provider.

### Speech-to-text
Answers are transcribed locally with [Whisper](https://github.com/SYSTRAN/faster-whisper): no API
key is needed and the audio never leaves your machine. The `small.en` model (~480 MB) is
downloaded on the first transcription; set the `WHISPER_MODEL` environment variable to use another one.

While you speak, live captions are shown: from the browser's Web Speech API in Chrome, Edge,
and Safari, and from the same local Whisper model in the desktop app and other browsers. Allow
camera and microphone access when asked.

### Text-to-speech
Questions are read aloud with a local [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) voice.
The question text stays hidden until you press "Show question", so each question is listening practice first.
Its model files (~350 MB) are downloaded in the background on first use, and rendered clips are cached in
`backend/data/tts/cache/`. Set the `TTS_VOICE` environment variable to change the voice. While the
download is running, or if the backend cannot produce audio, the browser's built-in voice is used instead.

### Feedback
After answering, "Get feedback" scores the attempt in two parts (0-100 each):
- **English**: grammar, vocabulary, and naturalness from the answer text, plus pronunciation,
  intonation, and stress from the audio. The audio scores need an LLM that accepts audio input
  (e.g. Gemini), and the answer audio is sent to that provider. With other models, Whisper's
  confidence in the words it heard is used as the pronunciation score instead.
- **Content**: relevance, structure, and specificity.

Written feedback is in the language picked under Settings ("Feedback language"). On first visit it starts from the browser's language.

### History
Every answer is saved with its transcript, scores, feedback, and a low-bitrate recording
(about 2 MB per minute) under `backend/data/`. The History page lists attempts by date and shows
how the scores changed against the previous attempt at the same question.

### Résumé and job postings
Upload a résumé (PDF, `.txt`, `.md`, or pasted text) and add job postings by link or pasted
text. For a link, the posting text is extracted from the page; pages that need a login or render
with JavaScript have to be pasted. Each posting has its own page with interview
questions generated for it at a chosen difficulty (easy, standard, or hard). A posting can use the
common résumé or its own (for applications tailored per company), plus an optional cover
letter. Follow-up questions and feedback for those questions take the posting and these
documents into account. Both are stored locally and their text is sent to the LLM for those requests.

## Tests
```bash
cd backend && uv run pytest     # API and logic, against a temporary data folder
cd frontend && npm test         # unit tests (Vitest)
```

The backend tests never call a real LLM, Whisper, or Kokoro, and never reach the network. Opening a pull
request into `main` runs both suites, the frontend build, and the desktop type check
(`.github/workflows/ci.yml`).

## Structure
- `backend/` — FastAPI app. Everything it stores lives in `backend/data/` (git-ignored): the SQLite file `app.db`, `recordings/`, and the `tts/` voice model and cache.
- `frontend/` — Vue 3 app; `/api` requests are proxied to the backend by Vite. Once built (`npm run build`), the backend serves it too, so http://127.0.0.1:8000 alone runs the whole app.
- `desktop/` — Electron shell that starts the backend and shows the app in a window.

## License
[MIT](LICENSE). Third-party work shipped in the built app — the libraries and the heading font, Bricolage
Grotesque (SIL Open Font License 1.1) — is credited in
[frontend/public/THIRD_PARTY_NOTICES.txt](frontend/public/THIRD_PARTY_NOTICES.txt), which is also served by the app at
`/THIRD_PARTY_NOTICES.txt`.
