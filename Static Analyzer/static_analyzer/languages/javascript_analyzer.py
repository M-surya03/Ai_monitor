"""
javascript_analyzer.py
----------------------
Regex-based static analysis for JavaScript / TypeScript source code.
Never calls ast.parse() — uses base_analyzer regex engine only.
Always returns full schema dict (same keys as all other analyzers).
"""

import logging
import re
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
LANG = "javascript"


def _js_loop_count(code: str) -> tuple:
    """
    Augment structural loop count with JS functional iteration methods
    (.forEach, .map, .filter, etc.) which imply O(n) passes.
    Structural depth is unchanged — functional methods do not nest.
    """
    structural_count, structural_depth = analyze_loops(code)
    functional = len(re.findall(
        r"\.(forEach|map|filter|reduce|find|findIndex|some|every)\s*\(",
        code,
    ))
    return structural_count + functional, structural_depth


def analyze(code: str) -> dict:
    """
    Run regex-based static analysis on JavaScript / TypeScript source code.

    Returns full schema dict — same shape as python_analyzer.analyze().
    api.py strips this down to the 5-field Spring Boot contract.
    """
    start = time.perf_counter()

    clean = strip_strings(strip_comments(code, LANG))

    syntax_issues              = check_syntax(code, LANG)
    loop_count, loop_depth     = _js_loop_count(clean)
    is_recursive               = detect_recursion(clean, LANG)
    has_halving                = detect_halving(clean)
    notation, complexity_notes = estimate_complexity(
        loop_count, loop_depth, is_recursive, has_halving
    )
    algorithm, pattern_desc, pattern_issues, suggestions = detect_pattern(
        clean, LANG, loop_count, loop_depth, is_recursive, has_halving,
    )

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