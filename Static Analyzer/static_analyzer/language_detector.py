"""
language_detector.py
--------------------
Auto-detects the programming language of submitted source code.

Supported languages: python, java, javascript, cpp
Falls back to 'unknown' when detection is inconclusive.
"""

import re
import logging
from typing import Literal

logger = logging.getLogger(__name__)

Language = Literal["python", "java", "javascript", "cpp", "unknown"]

# ── Per-language weighted signals ─────────────────────────────
_SIGNALS: dict[str, list[tuple[str, int]]] = {
    "python": [
        (r"\bdef\s+\w+\s*\(", 5),
        (r"\bimport\s+\w+",   3),
        (r"\bprint\s*\(",      3),
        (r":\s*$",             3),   # colon at end of line
        (r"\belif\b",          5),
        (r"\bNone\b",          3),
        (r"\bTrue\b|\bFalse\b",2),
        (r"#.*$",              2),   # hash comment
        (r"\brange\s*\(",      4),
        (r"\bself\b",          5),
    ],
    "java": [
        (r"\bpublic\s+(?:static\s+)?(?:void|int|String|boolean|class)\b", 6),
        (r"\bSystem\.out\.print",  5),
        (r"\bArrayList\b|\bHashMap\b", 5),
        (r";\s*$",                 2),   # semicolons
        (r"\bclass\s+\w+\s*\{",   4),
        (r"\bnew\s+\w+\s*\(",     3),
        (r"@Override\b",           5),
        (r"\bimport\s+java\.",     6),
        (r"\.length\b",            3),
        (r"\bString\[\]",          4),
    ],
    "javascript": [
        (r"\bconst\b|\blet\b|\bvar\b",  4),
        (r"\bconsole\.log\s*\(",        5),
        (r"=>\s*\{",                    5),   # arrow function
        (r"\bfunction\s+\w+\s*\(",      4),
        (r"\bdocument\.",               5),
        (r"\bPromise\b|\basync\b|\bawait\b", 4),
        (r"===|!==",                    4),
        (r"\brequire\s*\(",             4),
        (r"\bmodule\.exports\b",        5),
        (r"\.forEach\s*\(|\.map\s*\(|\.filter\s*\(", 4),
    ],
    "cpp": [
        (r"#include\s*<",              6),
        (r"\bstd::",                   6),
        (r"\bcout\s*<<",               5),
        (r"\bcin\s*>>",                5),
        (r"\bint\s+main\s*\(",         5),
        (r"\bvector\s*<",              4),
        (r"\bnamespace\s+\w+",         4),
        (r"\bnullptr\b",               4),
        (r"\bauto\b",                  2),
        (r"::\w+",                     3),
    ],
}


def detect_language(code: str) -> Language:
    """
    Detect the programming language from source code.

    Scores each language by counting weighted regex matches.
    Returns the highest-scoring language, or 'unknown' when
    no language scores above the minimum threshold.

    Args:
        code: Raw source code string.

    Returns:
        Language string: 'python' | 'java' | 'javascript' | 'cpp' | 'unknown'
    """
    if not code or not code.strip():
        return "unknown"

    scores: dict[str, int] = {lang: 0 for lang in _SIGNALS}

    for lang, signals in _SIGNALS.items():
        for pattern, weight in signals:
            matches = re.findall(pattern, code, re.MULTILINE)
            scores[lang] += len(matches) * weight

    logger.debug("Language detection scores: %s", scores)

    best_lang  = max(scores, key=lambda k: scores[k])
    best_score = scores[best_lang]

    if best_score < 4:
        return "unknown"

    return best_lang  # type: ignore[return-value]


def normalize_language(lang: str | None) -> Language:
    """
    Normalize a user-supplied language string to a canonical name.

    Accepts common aliases:
        'js', 'node', 'nodejs'    → 'javascript'
        'c++', 'cxx', 'cc'        → 'cpp'
        'py'                      → 'python'
    """
    if not lang:
        return "unknown"
    lang = lang.strip().lower()
    aliases: dict[str, Language] = {
        "python":     "python",
        "py":         "python",
        "java":       "java",
        "javascript": "javascript",
        "js":         "javascript",
        "node":       "javascript",
        "nodejs":     "javascript",
        "typescript": "javascript",
        "ts":         "javascript",
        "cpp":        "cpp",
        "c++":        "cpp",
        "cxx":        "cpp",
        "cc":         "cpp",
        "c":          "cpp",
    }
    return aliases.get(lang, "unknown")