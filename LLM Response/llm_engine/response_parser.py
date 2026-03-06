"""
response_parser.py
------------------
Extracts and validates the structured JSON payload from the raw LLM
text output.

LLMs frequently wrap their output in markdown code fences, add
preambles, or return partial JSON.  This module handles all of those
cases gracefully and always returns a dict that matches the contract
expected by Spring Boot.
"""

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ── Schema defaults ────────────────────────────────────────────
_FALLBACK: dict[str, Any] = {
    "algorithm_detected":  "Unknown",
    "time_complexity":     "Unknown",
    "space_complexity":    "Unknown",
    "problem":             "LLM response could not be parsed.",
    "explanation":         "",
    "suggested_algorithm": "",
    "improved_complexity": "",
    "improved_code":       "",
    "key_improvements":    [],
}

# Required fields that must be present for a result to be valid.
_REQUIRED_FIELDS = {
    "algorithm_detected",
    "time_complexity",
    "problem",
    "explanation",
    "improved_code",
}


# ══════════════════════════════════════════════════════════════
#  Extraction helpers
# ══════════════════════════════════════════════════════════════

def _strip_fences(text: str) -> str:
    """Remove markdown code fences: ```json ... ``` or ``` ... ```"""
    # Remove opening fence (with optional language tag)
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
    # Remove closing fence
    text = re.sub(r"\n?```$", "", text.strip())
    return text.strip()


def _extract_json_block(text: str) -> str | None:
    """
    Find the first {...} block in *text* using brace counting.
    Returns the raw JSON string or None if not found.
    """
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for i, ch in enumerate(text[start:], start=start):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None


def _sanitise(data: dict) -> dict:
    """
    Fill missing fields with fallback values and coerce types.
    """
    result = dict(_FALLBACK)      # start with all defaults
    result.update(data)           # overlay whatever the LLM returned

    # Coerce key_improvements to a list of strings
    ki = result.get("key_improvements", [])
    if isinstance(ki, str):
        result["key_improvements"] = [ki]
    elif not isinstance(ki, list):
        result["key_improvements"] = []

    # Ensure every string field is actually a string
    str_fields = [
        "algorithm_detected", "time_complexity", "space_complexity",
        "problem", "explanation", "suggested_algorithm",
        "improved_complexity", "improved_code",
    ]
    for field in str_fields:
        if not isinstance(result.get(field), str):
            result[field] = str(result.get(field, ""))

    return result


# ══════════════════════════════════════════════════════════════
#  Public API
# ══════════════════════════════════════════════════════════════

def parse_llm_response(raw_response: dict[str, Any]) -> dict[str, Any]:
    """
    Parse the Ollama API response dict into a clean, validated result.

    Strategy
    --------
    1. Extract the ``"response"`` text field from Ollama's envelope.
    2. Strip any markdown fences.
    3. Try ``json.loads()`` on the whole text.
    4. If that fails, extract the first ``{...}`` block and try again.
    5. If still failing, return a graceful fallback with the raw text
       in ``explanation`` so no information is lost.

    Args:
        raw_response: The dict returned by :func:`llm_client.call_llm`.

    Returns:
        Validated dict matching the LLM engine response schema.
    """
    raw_text: str = raw_response.get("response", "")

    if not raw_text.strip():
        logger.warning("LLM returned an empty response body.")
        fallback = dict(_FALLBACK)
        fallback["problem"] = "LLM returned an empty response."
        return fallback

    # ── Attempt 1: parse after stripping fences ────────────────
    cleaned = _strip_fences(raw_text)
    try:
        data = json.loads(cleaned)
        logger.debug("JSON parsed successfully on attempt 1 (full text).")
        return _sanitise(data)
    except json.JSONDecodeError:
        pass

    # ── Attempt 2: extract first {...} block ───────────────────
    json_block = _extract_json_block(cleaned)
    if json_block:
        try:
            data = json.loads(json_block)
            logger.debug("JSON parsed successfully on attempt 2 (extracted block).")
            return _sanitise(data)
        except json.JSONDecodeError as exc:
            logger.warning("JSON block found but failed to parse: %s", exc)

    # ── Attempt 3: graceful fallback ───────────────────────────
    logger.error(
        "Could not parse LLM response as JSON. Raw text (first 300 chars): %s",
        raw_text[:300],
    )
    fallback = dict(_FALLBACK)
    fallback["explanation"] = raw_text          # preserve the full LLM text
    fallback["problem"] = (
        "The LLM response was not valid JSON. "
        "The raw output is preserved in 'explanation'."
    )
    return fallback


def is_valid_result(result: dict[str, Any]) -> bool:
    """
    Return True if *result* contains all required fields with non-empty values.
    Useful for callers that want to decide whether to retry.
    """
    return all(
        result.get(field, "").strip() not in ("", "Unknown")
        for field in _REQUIRED_FIELDS
    )