"""One entry point for calling any LLM provider (via LiteLLM)."""

import os

import litellm
from pydantic import BaseModel, ValidationError

# Skip request parameters a given provider does not support instead of failing.
litellm.drop_params = True

SETUP_HINT = (
    "Set LLM_MODEL (e.g. gemini/<model>, openrouter/<vendor>/<model>) and that "
    "provider's API key in backend/.env, then restart the backend."
)

class LLMError(Exception):
    """Raised with a user-facing message when the model cannot produce a reply."""


def complete(system: str, user: str | list[dict], **params) -> str:
    """Send one system + user message and return the model's text reply.

    `user` is plain text, or a list of content parts when sending audio. Extra keyword
    arguments (e.g. response_format, timeout) are passed through to LiteLLM.
    """
    # "<provider>/<model>"; LiteLLM reads the matching provider key from the environment.
    model = os.environ.get("LLM_MODEL", "").strip()
    if not model:
        raise LLMError(f"No model is configured. {SETUP_HINT}")

    try:
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            **{
                # Providers return transient 429/503 under load; retry a couple of times.
                "num_retries": 2,
                # Fail fast instead of leaving the interview waiting on a stalled request.
                "timeout": 30,
                **params,
            },
        )
    except litellm.AuthenticationError as e:
        raise LLMError(f"The API key for {model} is missing or invalid. {SETUP_HINT}") from e
    except litellm.RateLimitError as e:
        raise LLMError("The LLM provider's rate limit was reached. Try again shortly.") from e
    except litellm.APIConnectionError as e:
        raise LLMError(f"Could not reach the LLM provider for {model}: {e}") from e
    except litellm.BadRequestError as e:
        # Includes an unknown provider prefix or model name.
        raise LLMError(f"The LLM provider rejected the request for {model}: {e}") from e
    except Exception as e:
        # LiteLLM's provider errors do not share one base class, so this is the boundary
        # that turns any remaining failure into a message for the UI.
        raise LLMError(f"LLM request failed for {model}: {e}") from e

    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise LLMError("The model returned an empty reply.")
    return text


def format_interview(turns: list[tuple[str, str]], background: str = "") -> str:
    """Render (question, answer) turns, preceded by the candidate's background if any."""
    transcript = "\n\n".join(
        f"Interviewer: {question}\nCandidate: {answer}" for question, answer in turns
    )
    if not background:
        return transcript
    return f"{background}\n\n<interview>\n{transcript}\n</interview>"


def parse_json_reply[T: BaseModel](reply: str, model: type[T]) -> T:
    """Validate a model's JSON reply against a schema."""
    # Some providers wrap JSON in a Markdown code fence.
    reply = reply.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
    try:
        return model.model_validate_json(reply)
    except ValidationError as e:
        raise LLMError(f"The model returned feedback in an unexpected format: {e}") from e
