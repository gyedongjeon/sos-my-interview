"""Follow-up question generation with any LLM provider (via LiteLLM)."""

import os

import litellm

# Skip request parameters a given provider does not support instead of failing.
litellm.drop_params = True

SETUP_HINT = (
    "Set LLM_MODEL (e.g. gemini/<model>, openrouter/<vendor>/<model>) and that "
    "provider's API key in backend/.env, then restart the backend."
)

SYSTEM_PROMPT = """\
You are an experienced interviewer running a mock job interview in English.
You will get the interview so far: the questions asked and the candidate's answers.
Ask exactly one follow-up question that digs deeper into the candidate's most recent
answer: probe a vague claim, a missing specific (numbers, their own role, the outcome),
or the reasoning behind a decision. Do not repeat a question that was already asked.

The answers are speech-recognition transcripts, so they may contain recognition errors
and no punctuation; read past those without commenting on them.

Reply with the question only, in one or two spoken-style sentences, with no preamble,
quotes, or formatting, because your reply is read aloud to the candidate as-is."""


class FollowUpError(Exception):
    """Raised with a user-facing message when a follow-up cannot be generated."""


def generate_follow_up(turns: list[tuple[str, str]]) -> str:
    """Return one follow-up question for a list of (question, answer) turns."""
    # "<provider>/<model>"; LiteLLM reads the matching provider key from the environment.
    model = os.environ.get("LLM_MODEL", "").strip()
    if not model:
        raise FollowUpError(f"No model is configured. {SETUP_HINT}")

    transcript = "\n\n".join(
        f"Interviewer: {question}\nCandidate: {answer}" for question, answer in turns
    )
    try:
        response = litellm.completion(
            model=model,
            max_tokens=4000,
            # A one-line question needs little reasoning; keep the wait short.
            reasoning_effort="low",
            # Providers return transient 429/503 under load; retry a couple of times.
            num_retries=2,
            # Fail fast instead of leaving the interview waiting on a stalled request.
            timeout=30,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
        )
    except litellm.AuthenticationError as e:
        raise FollowUpError(f"The API key for {model} is missing or invalid. {SETUP_HINT}") from e
    except litellm.RateLimitError as e:
        raise FollowUpError("The LLM provider's rate limit was reached. Try again shortly.") from e
    except litellm.APIConnectionError as e:
        raise FollowUpError(f"Could not reach the LLM provider for {model}: {e}") from e
    except litellm.BadRequestError as e:
        # Includes an unknown provider prefix or model name.
        raise FollowUpError(f"The LLM provider rejected the request for {model}: {e}") from e
    except Exception as e:
        # LiteLLM's provider errors do not share one base class, so this is the boundary
        # that turns any remaining failure into a message for the UI.
        raise FollowUpError(f"LLM request failed for {model}: {e}") from e

    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise FollowUpError("The model returned an empty follow-up question.")
    return text
