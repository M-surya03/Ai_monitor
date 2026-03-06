"""
llm_client.py
-------------
Calls the Groq API using the official groq Python SDK.

Features
--------
- Automatic retry with exponential back-off on transient errors.
- Structured logging at every stage.
- Clean error types so callers can handle failures precisely.
- Health-check helper.
"""

import logging
import time
from typing import Any

from groq import Groq, APIConnectionError, APIStatusError, RateLimitError

from .config import GROQ_API_KEY, MAX_RETRIES, MAX_TOKENS, MODEL_NAME, TEMPERATURE, TIMEOUT

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
#  Custom exceptions
# ══════════════════════════════════════════════════════════════

class GroqUnavailableError(RuntimeError):
    """Raised when Groq API cannot be reached after all retries."""

class GroqResponseError(RuntimeError):
    """Raised when Groq returns an unexpected API error."""


# ══════════════════════════════════════════════════════════════
#  Client
# ══════════════════════════════════════════════════════════════

def _get_client() -> Groq:
    if not GROQ_API_KEY:
        raise GroqUnavailableError(
            "GROQ_API_KEY is not set. "
            "Get your free key at https://console.groq.com and set it:\n"
            "  Windows:  $env:GROQ_API_KEY='gsk_...'\n"
            "  Linux/Mac: export GROQ_API_KEY='gsk_...'"
        )
    return Groq(api_key=GROQ_API_KEY, timeout=TIMEOUT)


def call_llm(prompt: str) -> dict[str, Any]:
    """
    Send *prompt* to Groq and return a normalised response dict.

    The returned dict matches the same shape as the old Ollama response
    so response_parser.py works without any changes:
        { "response": "<llm text output>" }

    Args:
        prompt: Fully formatted prompt string.

    Returns:
        Dict with key ``"response"`` containing the model's text output,
        plus ``"model"``, ``"eval_count"`` metadata.

    Raises:
        GroqUnavailableError: API key missing or network unreachable.
        GroqResponseError:    Groq returned an API error.
        ValueError:           Prompt is empty.
    """
    if not prompt or not prompt.strip():
        raise ValueError("call_llm: prompt must not be empty.")

    client     = _get_client()
    last_exc: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(
                "Groq request attempt %d/%d — model=%s",
                attempt, MAX_RETRIES, MODEL_NAME,
            )
            start = time.perf_counter()

            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior software engineer and algorithm expert. "
                            "You always respond with ONLY a valid JSON object. "
                            "No markdown fences, no preamble, no explanation outside the JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )

            elapsed = (time.perf_counter() - start) * 1_000
            text    = completion.choices[0].message.content or ""
            tokens  = completion.usage.completion_tokens if completion.usage else 0

            logger.info(
                "Groq response received in %.0f ms — tokens=%d",
                elapsed, tokens,
            )

            # Normalise to the same shape response_parser expects
            return {
                "response":   text,
                "model":      completion.model,
                "eval_count": tokens,
            }

        except RateLimitError as exc:
            last_exc = exc
            wait = 2 ** attempt
            logger.warning("Groq rate limit hit — retrying in %ds", wait)
            if attempt < MAX_RETRIES:
                time.sleep(wait)

        except APIConnectionError as exc:
            last_exc = exc
            wait = 2 ** (attempt - 1)
            logger.warning(
                "Groq connection error on attempt %d — retrying in %ds (%s)",
                attempt, wait, exc,
            )
            if attempt < MAX_RETRIES:
                time.sleep(wait)

        except APIStatusError as exc:
            if exc.status_code and 500 <= exc.status_code < 600:
                last_exc = exc
                wait = 2 ** (attempt - 1)
                logger.warning(
                    "Groq 5xx (%d) on attempt %d — retrying in %ds",
                    exc.status_code, attempt, wait,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(wait)
            else:
                raise GroqResponseError(
                    f"Groq API error {exc.status_code}: {exc.message}"
                ) from exc

    raise GroqUnavailableError(
        f"Groq did not respond after {MAX_RETRIES} attempts. "
        f"Last error: {last_exc}"
    )


def health_check() -> bool:
    """Return True if the Groq API key is set and the SDK can initialise."""
    try:
        _get_client()
        return bool(GROQ_API_KEY)
    except Exception:
        return False