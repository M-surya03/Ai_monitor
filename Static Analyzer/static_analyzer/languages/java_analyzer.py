"""
java_analyzer.py
----------------
Regex-based static analysis for Java source code.
Never calls ast.parse() — uses base_analyzer regex engine only.
Always returns full schema dict (same keys as all other analyzers).
"""

import logging
import time

from .base_analyzer import (
    AnalysisResult,
    analyze_loops,
    check_syntax,
    detect_halving,
    detect_pattern,
    detect_recursion,
    estimate_complexity,
    strip_comments,
    strip_strings,
)

logger = logging.getLogger(__name__)
LANG = "java"


def analyze(code: str) -> dict:
    """
    Run regex-based static analysis on Java source code.

    Returns full schema dict — same shape as python_analyzer.analyze().
    api.py strips this down to the 5-field Spring Boot contract.
    """
    start = time.perf_counter()

    # ── Pre-process: remove comments and string literals ──────
    clean = strip_strings(strip_comments(code, LANG))

    # ── Syntax validation ─────────────────────────────────────
    syntax_issues = check_syntax(code, LANG)

    # ── Structural analysis ───────────────────────────────────
    loop_count, loop_depth = analyze_loops(clean)
    is_recursive            = detect_recursion(clean, LANG)
    has_halving             = detect_halving(clean)

    # ── Complexity estimation ─────────────────────────────────
    notation, complexity_notes = estimate_complexity(
        loop_count, loop_depth, is_recursive, has_halving
    )

    # ── Algorithm pattern detection ───────────────────────────
    algorithm, pattern_desc, pattern_issues, suggestions = detect_pattern(
        clean, LANG, loop_count, loop_depth, is_recursive, has_halving,
    )

    # ── Merge issues (syntax first, then algorithmic) ─────────
    all_issues = list(dict.fromkeys(syntax_issues + pattern_issues))
    all_sugg   = list(dict.fromkeys(suggestions + complexity_notes))
    elapsed_ms = (time.perf_counter() - start) * 1_000

    return AnalysisResult(
        algorithm_detected  = algorithm,
        time_complexity     = notation,
        issues              = all_issues,
        loop_count          = loop_count,
        pattern             = pattern_desc,
        suggestions         = all_sugg,
        complexity_notes    = complexity_notes,
        loop_depth          = loop_depth,
        is_recursive        = is_recursive,
        has_halving_pattern = has_halving,
        elapsed_ms          = elapsed_ms,
    ).to_dict()