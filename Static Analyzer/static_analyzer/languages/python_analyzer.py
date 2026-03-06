"""
python_analyzer.py
------------------
Delegates to the original AST-based pipeline for maximum Python accuracy.

Syntax errors are surfaced inside 'issues' — never as a fatal top-level error —
so the output shape is always identical to the other language analyzers.
"""

import logging
import time

logger = logging.getLogger(__name__)


def analyze(code: str) -> dict:
    """Full AST-based analysis for Python source code. Returns full schema dict."""
    from ..ast_parser          import parse_code
    from ..complexity_analyzer import analyze_complexity
    from ..pattern_detector    import detect_pattern
    from ..utils               import (
        build_error_response, build_success_response,
        CodeTooLargeError, validate_code_input,
    )

    start = time.perf_counter()

    # ── Input validation ──────────────────────────────────────
    try:
        clean = validate_code_input(code)
    except (TypeError, ValueError, CodeTooLargeError) as exc:
        return build_error_response(str(exc))

    # ── Parse — surface syntax errors inside issues ───────────
    tree, parse_error = parse_code(clean)
    if parse_error is not None:
        line_info = f" (line {parse_error.line})" if parse_error.line else ""
        text_info = f": `{parse_error.text.strip()}`" if parse_error.text else ""
        return build_success_response(
            algorithm_detected  = "Unknown",
            time_complexity     = "Unknown",
            issues              = [
                f"Syntax error{line_info}{text_info} \u2014 {parse_error.message}",
                "Fix the syntax error before re-analysing.",
            ],
            loop_count          = 0,
            pattern             = "parse failed",
            elapsed_ms          = (time.perf_counter() - start) * 1_000,
        )

    # ── Complexity analysis ───────────────────────────────────
    try:
        complexity = analyze_complexity(tree)
    except Exception as exc:
        return build_error_response(f"Complexity analysis failed: {exc}")

    # ── Pattern detection ─────────────────────────────────────
    try:
        pattern = detect_pattern(tree)
    except Exception as exc:
        return build_error_response(f"Pattern detection failed: {exc}")

    merged_issues      = list(dict.fromkeys(pattern.issues))
    merged_suggestions = list(dict.fromkeys(pattern.suggestions + complexity.notes))
    elapsed_ms         = (time.perf_counter() - start) * 1_000

    return build_success_response(
        algorithm_detected  = pattern.algorithm,
        time_complexity     = complexity.notation,
        issues              = merged_issues,
        loop_count          = pattern.loop_count,
        pattern             = pattern.pattern,
        suggestions         = merged_suggestions,
        complexity_notes    = complexity.notes,
        loop_depth          = complexity.loop_depth,
        is_recursive        = complexity.is_recursive,
        has_halving_pattern = complexity.has_halving_pattern,
        elapsed_ms          = elapsed_ms,
    )