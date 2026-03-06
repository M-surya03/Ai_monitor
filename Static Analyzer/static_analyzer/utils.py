"""
utils.py
--------
Shared utilities for the static_analyzer package.

Includes:
  - Logging configuration
  - Input sanitisation / size guard
  - Response schema builder
  - Execution-time decorator
"""

import functools
import logging
import time
from typing import Any, Callable

# ──────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────

def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure root-level logging for the analyzer package.

    Should be called once at application startup.  If your host framework
    (e.g. Spring Boot's embedded Jython, or a Flask/FastAPI wrapper) already
    configures logging, you may skip this call.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


# ──────────────────────────────────────────────────────────────
# Input validation
# ──────────────────────────────────────────────────────────────

#: Hard limit on accepted code size (characters).  Prevents abuse / DoS.
MAX_CODE_LENGTH: int = 50_000


class CodeTooLargeError(ValueError):
    """Raised when submitted code exceeds :data:`MAX_CODE_LENGTH`."""


def validate_code_input(code: Any) -> str:
    """
    Validate and normalise the raw code input.

    Args:
        code: Arbitrary input — expected to be a non-empty string.

    Returns:
        Stripped code string.

    Raises:
        TypeError: If *code* is not a string.
        ValueError: If *code* is empty.
        CodeTooLargeError: If *code* exceeds :data:`MAX_CODE_LENGTH`.
    """
    if not isinstance(code, str):
        raise TypeError(f"Expected str, got {type(code).__name__!r}.")
    stripped = code.strip()
    if not stripped:
        raise ValueError("Code input must not be empty.")
    if len(stripped) > MAX_CODE_LENGTH:
        raise CodeTooLargeError(
            f"Code length {len(stripped):,} exceeds maximum allowed "
            f"{MAX_CODE_LENGTH:,} characters."
        )
    return stripped


# ──────────────────────────────────────────────────────────────
# Response helpers
# ──────────────────────────────────────────────────────────────

def build_error_response(message: str, details: dict | None = None) -> dict:
    """
    Build a standardised error response payload.

    Args:
        message: Human-readable error description.
        details: Optional extra context (e.g. line / offset from a SyntaxError).

    Returns:
        Dict with ``"error"`` key and optional ``"details"`` sub-dict.
    """
    payload: dict[str, Any] = {"error": message}
    if details:
        payload["details"] = details
    return payload


def build_success_response(
    algorithm_detected: str,
    time_complexity: str,
    issues: list[str],
    loop_count: int,
    pattern: str,
    *,
    suggestions: list[str] | None = None,
    complexity_notes: list[str] | None = None,
    loop_depth: int = 0,
    is_recursive: bool = False,
    has_halving_pattern: bool = False,
    elapsed_ms: float = 0.0,
) -> dict:
    """
    Build the canonical response schema.

    'issues' contains algorithmic findings + suggestions + complexity notes
    + structural metadata (loop depth, recursion flag, halving, elapsed time).

    All other fields are ALSO kept as top-level keys so run.py can display
    them directly and api.py can whitelist just the 5-field Spring Boot contract.
    """
    all_issues = list(issues)

    for item in (suggestions or []):
        if item and item not in all_issues:
            all_issues.append(item)

    for item in (complexity_notes or []):
        if item and item not in all_issues:
            all_issues.append(item)

    if loop_depth > 0:
        note = f"Loop depth: {loop_depth}"
        if note not in all_issues:
            all_issues.append(note)

    if is_recursive:
        note = "Recursive function detected"
        if note not in all_issues:
            all_issues.append(note)

    if has_halving_pattern:
        note = "Halving pattern detected (e.g. binary search step)"
        if note not in all_issues:
            all_issues.append(note)

    if elapsed_ms > 0:
        note = f"Analyzed in {round(elapsed_ms, 2)} ms"
        if note not in all_issues:
            all_issues.append(note)

    # ── Return FULL schema (api.py filters to 5 fields for Spring Boot) ──
    return {
        "algorithm_detected":  algorithm_detected,
        "time_complexity":     time_complexity,
        "issues":              all_issues,
        "loop_count":          loop_count,
        "pattern":             pattern,
        # ── Extra fields for run.py display — stripped by api.py ──────────
        "loop_depth":          loop_depth,
        "is_recursive":        is_recursive,
        "has_halving_pattern": has_halving_pattern,
        "elapsed_ms":          round(elapsed_ms, 3),
    }