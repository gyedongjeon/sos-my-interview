---
title: "test: add live LLM tests and a development .env"
date: 2026-11-21
branch: chore/env-file
request-source: chat session, 2026-11-21
---

## Request

Bring back a `.env` file with an example, so that a test key can be kept locally, and add a few
simple tests that call a real LLM, run in CI with a key kept as a GitHub secret.

## Changes

- **Live tests**: three backend tests marked `live` send real requests through the API: a
  follow-up question, scored feedback in Korean, and questions for a job posting. Replies
  differ every time, so they check the shape only (status, score ranges, required fields, the
  feedback language). They are left out of a normal `pytest` run, run with `pytest -m live`,
  and skip themselves when the provider key is not set.
- **CI**: `ci.yml` has a separate "Backend (live LLM)" job that gets `GEMINI_API_KEY` from a
  repository secret. It is separate so that a provider outage is not mistaken for a broken
  test. The release workflow calls `ci.yml` without passing secrets, so the live tests skip
  there and cannot block a release.
- **A bug the live tests found**: with an invalid key, the error shown was "tenacity import
  failed". LiteLLM retries failed requests (`num_retries`) with `tenacity` but does not install
  it, so every failed request was reported as that instead of its real cause, and nothing was
  retried. `tenacity` is now a dependency, with a test that it is present.
- **`backend/.env.example`**: a commented template with the model, the provider key variables,
  and the optional settings the backend already reads. It holds no keys; `.env` stays
  git-ignored. No loading code was added: uv loads the file with `uv run --env-file .env ...`.
- **Tests no longer read a developer's `.env`**: LiteLLM loads `.env` from the working folder
  when it is imported, which made three existing tests fail as soon as `backend/.env` had a
  model in it. The test setup now sets `LITELLM_MODE=PRODUCTION`, which turns that off.
- **Priority is unchanged**: a model and key saved on the Settings page still win over the
  environment. The packaged app has no `.env`.

## Verification

- `uv run pytest`: 81 passed, 3 deselected. The test for `tenacity` failed before the
  dependency was added.
- `uv run pytest -m live` without a key: 3 skipped, with the reason shown.
- `uv run --env-file .env pytest -m live` with a real key: 3 passed in about 8 seconds.
- With an invalid key, the endpoints now answer "The API key ... is missing or invalid" instead
  of the tenacity message.
- A backend started with `--env-file` on an empty data folder reported the model from the file
  as coming from the environment.
- Not verified until the pull request is opened: the live job in GitHub Actions with the
  secret.
