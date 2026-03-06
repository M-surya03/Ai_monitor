"""
analyzer.py
-----------
Public entry point for the multi-language static_analyzer package.

    from static_analyzer import analyze_code

    # Auto-detect language
    result = analyze_code(source_code)

    # Explicit language
    result = analyze_code(source_code, language="java")

Supported languages: python, java, javascript (js), cpp (c++)

The returned dict always conforms to one of two shapes:

Success::

    {
        "algorithm_detected": str,
        "time_complexity":    str,
        "issues":             list[str],   # syntax errors appear here too
        "loop_count":         int,
        "pattern":            str,
        "suggestions":        list[str],
        "complexity_notes":   list[str],
        "loop_depth":         int,
        "is_recursive":       bool,
        "has_halving_pattern":bool,
        "elapsed_ms":         float,
        "language":           str,
    }

Error::

    {
        "error":    str,
        "language": str,
    }
"""

import logging
from typing import Optional

from .language_detector import detect_language, normalize_language
from .utils import build_error_response

logger = logging.getLogger(__name__)


def analyze_code(code: object, language: Optional[str] = None) -> dict:
    """
    Analyse source code in any supported language.

    Args:
        code:     Source code as a plain string.
        language: Optional language hint. If None, auto-detected.
                  Accepted values: 'python', 'java', 'javascript',
                  'js', 'cpp', 'c++', 'typescript', 'ts', 'py'

    Returns:
        Result dict with 'language' field added.
        Never raises — all errors become structured payloads.
    """
    import time
    start = time.perf_counter()

    # ── 1. Basic input guard ──────────────────────────────────
    if not isinstance(code, str):
        return {**build_error_response(
            f"Expected str, got {type(code).__name__!r}."
        ), "language": "unknown"}

    if not code.strip():
        return {**build_error_response(
            "Code input must not be empty."
        ), "language": "unknown"}

    if len(code) > 50_000:
        return {**build_error_response(
            f"Code length {len(code):,} exceeds the 50,000-character limit."
        ), "language": "unknown"}

    # ── 2. Language resolution ────────────────────────────────
    if language:
        lang = normalize_language(language)
        if lang == "unknown":
            logger.warning("Unrecognised language hint %r — auto-detecting.", language)
            lang = detect_language(code)
    else:
        lang = detect_language(code)

    if lang == "unknown":
        # Fall back to Python analyzer for unrecognised code
        logger.info("Language unknown — defaulting to Python analyzer.")
        lang = "python"

    logger.info("Analyzing code as language=%s (%d chars)", lang, len(code))

    # ── 3. Route to language-specific analyzer ────────────────
    try:
        result = _dispatch(code, lang)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error in %s analyzer.", lang)
        return {
            **build_error_response(f"Analysis failed: {exc}"),
            "language": lang,
        }

    # ── 4. Attach language tag ────────────────────────────────
    result["language"] = lang
    return result


def _dispatch(code: str, lang: str) -> dict:
    """Route to the correct language analyzer."""
    if lang == "python":
        from .languages.python_analyzer     import analyze
    elif lang == "java":
        from .languages.java_analyzer       import analyze
    elif lang == "javascript":
        from .languages.javascript_analyzer import analyze
    elif lang == "cpp":
        from .languages.cpp_analyzer        import analyze
    else:
        from .languages.python_analyzer     import analyze

    return analyze(code)