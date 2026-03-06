"""
engine.py
---------
Main coordinator for the LLM engine (Groq-powered).
"""

import logging
import time
from typing import Any

from .llm_client import GroqUnavailableError, GroqResponseError, call_llm, health_check
from .prompt_builder import build_prompt
from .response_parser import is_valid_result, parse_llm_response

logger = logging.getLogger(__name__)


def run_llm_analysis(code: str, static_result: dict[str, Any]) -> dict[str, Any]:
    """Full LLM analysis pipeline. Never raises — errors become structured payloads."""
    start = time.perf_counter()

    if not code or not code.strip():
        return _error_response("Code input is empty.", start)

    if not isinstance(static_result, dict):
        return _error_response("static_result must be a dict.", start)

    try:
        prompt = build_prompt(code, static_result)
    except ValueError as exc:
        return _error_response(f"Prompt build error: {exc}", start)

    try:
        raw_response = call_llm(prompt)
    except GroqUnavailableError as exc:
        return _error_response(str(exc), start, api_down=True)
    except GroqResponseError as exc:
        return _error_response(str(exc), start)
    except Exception as exc:
        logger.exception("Unexpected LLM error.")
        return _error_response(f"Unexpected error: {exc}", start)

    result = parse_llm_response(raw_response)

    from .config import MODEL_NAME
    elapsed_ms = round((time.perf_counter() - start) * 1_000, 2)
    result["elapsed_ms"]    = elapsed_ms
    result["llm_model"]     = MODEL_NAME
    result["parse_success"] = is_valid_result(result)

    logger.info(
        "LLM analysis complete — algorithm=%s complexity=%s elapsed=%.0fms",
        result.get("algorithm_detected"),
        result.get("time_complexity"),
        elapsed_ms,
    )
    return result


def check_groq_health() -> dict[str, Any]:
    from .config import MODEL_NAME, GROQ_API_KEY
    up = health_check()
    return {
        "groq_available": up,
        "model":          MODEL_NAME,
        "api_key_set":    bool(GROQ_API_KEY),
        "status":         "ok" if up else "GROQ_API_KEY not set",
    }


# keep old name for backwards compat
check_ollama_health = check_groq_health


def _error_response(message: str, start: float, api_down: bool = False) -> dict[str, Any]:
    from .config import MODEL_NAME
    return {
        "error":               message,
        "api_down":            api_down,
        "algorithm_detected":  "Unknown",
        "time_complexity":     "Unknown",
        "space_complexity":    "Unknown",
        "problem":             message,
        "explanation":         "",
        "suggested_algorithm": "",
        "improved_complexity": "",
        "improved_code":       "",
        "key_improvements":    [],
        "elapsed_ms":          round((time.perf_counter() - start) * 1_000, 2),
        "llm_model":           MODEL_NAME,
        "parse_success":       False,
    }