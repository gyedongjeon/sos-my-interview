# Agent Instructions

This file provides specific context and operational rules for AI assistants working within the `sos-my-interview` project.

## Core Directives
- **Source of Truth**: Always refer to the following documents for project rules and conventions:
    - [docs/git-workflow/commit-convention.md](docs/git-workflow/commit-convention.md) - Rules for commit messages.
    - [docs/git-workflow/branching-strategy.md](docs/git-workflow/branching-strategy.md) - Branch naming and GitHub Flow / merge strategy.
    - [docs/git-workflow/pr-convention.md](docs/git-workflow/pr-convention.md) - PR title, description, and process conventions.
    - [docs/git-workflow/versioning.md](docs/git-workflow/versioning.md) - Semantic Versioning rules, version files, and release tags.
    - [README.md](README.md) - Project overview and structure.
- **Commits**: Use Conventional Commits as defined in [docs/git-workflow/commit-convention.md](docs/git-workflow/commit-convention.md).
- **Language**: Documentation and code comments should be in **English**. User interaction can be in Korean or English as per user preference.
- **Security & Data Protection**: Never add secrets, API keys, credentials, or personal data to the repository. Worklog/PR text also follows the anonymization rules in **Worklog**.

## Development Method
Follow Kent Beck's Test-Driven Development and Tidy First.

- **TDD (Red → Green → Refactor)**:
    - Write one small failing test first, and run it to see it fail for the expected reason.
    - Write the least code that makes it pass, then refactor with all tests passing.
    - Add one test at a time. Name a test after the behavior it describes (e.g. `test_saved_key_is_never_sent_back`).
    - For a bug, first write a test that reproduces it, then fix it.
    - Run the whole suite before every commit; never commit with a failing test.
- **Tidy First (separate structural from behavioral changes)**:
    - A **structural** change rearranges code without changing what it does (rename, extract, move, reorder). A **behavioral** change adds or alters functionality.
    - Never mix the two in one commit. When both are needed, tidy first: make the structural change, confirm the tests still pass, commit it, then make the behavioral change.
    - Commit structural changes as `refactor:` and behavioral ones as `feat:` or `fix:`, per the commit convention.
    - Tidy only what makes the next change easier; keep each tidying small.
- **Running the tests**:
    - Backend: `cd backend && uv run pytest`. Tests use a temporary data folder and block network access; mock the LLM, Whisper, and Kokoro instead of calling them.
    - Frontend: `cd frontend && npm test` (Vitest), and `npm run build` for the type check.
    - Desktop: `cd desktop && npm test` (Vitest), and `npx tsc --noEmit` for the type check.
    - `.github/workflows/ci.yml` runs all of these when a pull request into `main` is opened. It does not run again on later pushes, so run the tests locally before pushing a fix (it can also be started by hand from the Actions tab).

## Worklog (MANDATORY for every PR)
- Every PR must include exactly one branch-specific worklog file named `docs/worklog/YYYY-MM-DD-<branch-slug>.md`. This count excludes [docs/worklog/_template.md](docs/worklog/_template.md).
- Create the worklog file on the same branch as the change and commit it **before opening the PR**.
- **The worklog file is the source of truth for the PR**: PR title = the worklog `title` field; PR description = the worklog body (from `## Request` down). Generate the PR from the file, never the other way around.
- If the scope changes during review, update the worklog file first, then sync the PR description to match.
- The Security & Data Protection rules apply to worklog files too. Never name individuals — including requesters or reviewers — in a worklog. Refer to request sources by channel/system and date, not by name.
- Never modify another branch's worklog file.

## Project Mission
- **Project**: `sos-my-interview` — a web-based mock interview service for personal use.
- **Architecture**: Separate frontend and backend.
    - **Backend**: FastAPI (Python) with SQLite as the database.
    - **Frontend**: Vue 3 + TypeScript + Vite, with Vue Router and Pinia. Styling uses Tailwind CSS with daisyUI as the design system; prefer daisyUI component classes and theme colors over custom CSS.
    - **Desktop**: Electron shell (`desktop/`, TypeScript) that runs the backend, which serves the built frontend.
- **Scope**: Runs locally for a single user. Do not add deployment, authentication, or multi-user features unless explicitly requested.

## Operational Preferences
- **Conciseness**: Be concise and technical in your responses.
