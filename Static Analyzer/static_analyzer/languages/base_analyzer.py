"""
base_analyzer.py
----------------
Shared regex-based analysis engine for Java, JavaScript, and C++.

Design contract
---------------
Every analyzer returns a FULL schema dict (all fields present).
api.py is the only place that filters to the 5-field Spring Boot contract.
run.py reads loop_depth / is_recursive / elapsed_ms directly for display.

Full schema:
    algorithm_detected   str
    time_complexity      str
    issues               list[str]   ← algorithmic + syntax + suggestions + notes + metadata
    loop_count           int
    pattern              str
    loop_depth           int
    is_recursive         bool
    has_halving_pattern  bool
    elapsed_ms           float
"""

import re
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
#  AnalysisResult dataclass
# ══════════════════════════════════════════════════════════════

@dataclass
class AnalysisResult:
    algorithm_detected:  str
    time_complexity:     str
    issues:              list
    loop_count:          int
    pattern:             str
    suggestions:         list  = field(default_factory=list)
    complexity_notes:    list  = field(default_factory=list)
    loop_depth:          int   = 0
    is_recursive:        bool  = False
    has_halving_pattern: bool  = False
    elapsed_ms:          float = 0.0

    def to_dict(self) -> dict:
        """
        Return the FULL schema dict.

        'issues' contains: algorithmic issues + suggestions + complexity notes
        + structural metadata (loop depth, recursion, halving, elapsed time).

        All other fields are ALSO kept as top-level keys so run.py
        can display them and api.py can filter to the 5-field contract.
        """
        all_issues = list(self.issues)

        for item in self.suggestions:
            if item and item not in all_issues:
                all_issues.append(item)

        for item in self.complexity_notes:
            if item and item not in all_issues:
                all_issues.append(item)

        if self.loop_depth > 0:
            note = f"Loop depth: {self.loop_depth}"
            if note not in all_issues:
                all_issues.append(note)

        if self.is_recursive:
            note = "Recursive function detected"
            if note not in all_issues:
                all_issues.append(note)

        if self.has_halving_pattern:
            note = "Halving pattern detected (e.g. binary search step)"
            if note not in all_issues:
                all_issues.append(note)

        if self.elapsed_ms > 0:
            note = f"Analyzed in {round(self.elapsed_ms, 2)} ms"
            if note not in all_issues:
                all_issues.append(note)

        # ── Return FULL schema (api.py filters to 5 fields for Spring Boot) ──
        return {
            "algorithm_detected":  self.algorithm_detected,
            "time_complexity":     self.time_complexity,
            "issues":              all_issues,
            "loop_count":          self.loop_count,
            "pattern":             self.pattern,
            # ── Extra fields for run.py display — stripped by api.py ──────────
            "loop_depth":          self.loop_depth,
            "is_recursive":        self.is_recursive,
            "has_halving_pattern": self.has_halving_pattern,
            "elapsed_ms":          round(self.elapsed_ms, 3),
        }


# ══════════════════════════════════════════════════════════════
#  Code pre-processing
# ══════════════════════════════════════════════════════════════

def strip_comments(code: str, lang: str) -> str:
    """Remove comments so they do not pollute pattern detection."""
    if lang in ("java", "cpp", "javascript"):
        code = re.sub(r"/\*.*?\*/", " ", code, flags=re.DOTALL)
        code = re.sub(r"//.*$",    " ", code, flags=re.MULTILINE)
    elif lang == "python":
        code = re.sub(r"#.*$",        " ", code, flags=re.MULTILINE)
        code = re.sub(r'""".*?"""',   " ", code, flags=re.DOTALL)
        code = re.sub(r"'''.*?'''",   " ", code, flags=re.DOTALL)
    return code


def strip_strings(code: str) -> str:
    """Replace string literals with empty placeholders."""
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
    code = re.sub(r"'(?:[^'\\]|\\.)*'", "''", code)
    return code


# ══════════════════════════════════════════════════════════════
#  Loop analysis  (brace-aware — function/class braces ignored)
# ══════════════════════════════════════════════════════════════

_LOOP_RE  = re.compile(r"\b(for|while|do)\b")
_OPEN_RE  = re.compile(r"\{")
_CLOSE_RE = re.compile(r"\}")


def analyze_loops(code: str) -> tuple:
    """
    Return (total_loop_count, max_nesting_depth).

    Brace-aware: only braces that belong to loop bodies contribute to depth,
    so class/function braces do NOT inflate the nesting count.
    """
    clean = strip_strings(code)

    events = []
    for m in _LOOP_RE.finditer(clean):
        events.append((m.start(), "loop"))
    for m in _OPEN_RE.finditer(clean):
        events.append((m.start(), "open"))
    for m in _CLOSE_RE.finditer(clean):
        events.append((m.start(), "close"))
    events.sort()

    brace_depth  = 0
    loop_stack   = []   # brace depths at which each loop opened
    pending_loop = False
    total_loops  = 0
    max_depth    = 0

    for _pos, kind in events:
        if kind == "loop":
            pending_loop = True
            total_loops += 1
        elif kind == "open":
            brace_depth += 1
            if pending_loop:
                loop_stack.append(brace_depth)
                if len(loop_stack) > max_depth:
                    max_depth = len(loop_stack)
                pending_loop = False
        elif kind == "close":
            if loop_stack and brace_depth == loop_stack[-1]:
                loop_stack.pop()
            brace_depth = max(brace_depth - 1, 0)

    # Brace-less single-line loops (e.g. C++ for without {})
    if total_loops > 0 and max_depth == 0:
        max_depth = 1

    return total_loops, max_depth


# ══════════════════════════════════════════════════════════════
#  Feature detectors
# ══════════════════════════════════════════════════════════════

def detect_swap(code: str) -> bool:
    """Detect variable swap patterns (temp var, tuple swap, std::swap, XOR)."""
    patterns = [
        r"\btemp\b\s*=",
        r"\w+\s*,\s*\w+\s*=\s*\w+\s*,\s*\w+",   # Python tuple swap
        r"\bstd::swap\s*\(|\bswap\s*\(",
        r"\w+\s*\^=\s*\w+",                        # XOR swap
        r"\bint\s+temp\b",
    ]
    return any(re.search(p, code, re.IGNORECASE) for p in patterns)


def detect_inner_loop_swap(code: str) -> bool:
    """True when a swap appears inside an inner-loop body (bubble sort signal)."""
    for m in re.finditer(r"\b(for|while)\b", code):
        segment = code[m.start(): m.start() + 600]
        if detect_swap(segment):
            return True
    return False


def detect_halving(code: str) -> bool:
    """Detect binary-search halving: mid = .../2, >>1, lo/hi pattern."""
    patterns = [
        r"\bmid\b\s*=\s*[^;]{0,40}/\s*2",
        r"\bmid\b\s*=\s*[^;]{0,40}>>\s*1",
        r"\blo\b[^;]{0,60}\bhi\b|\bleft\b[^;]{0,60}\bright\b",
        r"Math\.floor\s*\([^)]{0,40}/\s*2\s*\)",
        r"[a-zA-Z_]\w*\s*/=\s*2",
        r"[a-zA-Z_]\w*\s*>>=\s*1",
    ]
    return any(re.search(p, code, re.IGNORECASE) for p in patterns)


def detect_recursion(code: str, lang: str) -> bool:
    """Detect self-recursive calls: find function defs, check if called inside body."""
    if lang == "python":
        defs = re.findall(r"def\s+(\w+)\s*\(", code)
    else:
        defs = re.findall(
            r"(?:int|void|bool|boolean|String|auto|double|float|long|char)\s+(\w+)\s*\(",
            code,
        )
    skip = {"main", "int", "void", "bool", "boolean"}
    for name in defs:
        if name in skip:
            continue
        calls = re.findall(rf"\b{re.escape(name)}\s*\(", code)
        if len(calls) >= 2:   # 1 definition + ≥1 recursive call
            return True
    return False


def detect_queue_usage(code: str) -> bool:
    patterns = [
        r"\bQueue\b|\bDeque\b|\bLinkedList\b",
        r"\bdeque\b",
        r"\.shift\s*\(\)",
        r"\bpopleft\s*\(\)",
        r"\bstd::queue\b|\bstd::deque\b",
    ]
    return any(re.search(p, code, re.IGNORECASE) for p in patterns)


def detect_stack_usage(code: str) -> bool:
    patterns = [
        r"\bStack\b|\bArrayDeque\b",
        r"\bstd::stack\b",
    ]
    return any(re.search(p, code, re.IGNORECASE) for p in patterns)


def detect_dp_structure(code: str, loop_depth: int) -> bool:
    has_table = bool(re.search(r"\bdp\b|\bmemo\b|\btable\b|\bcache\b", code, re.IGNORECASE))
    return has_table and loop_depth >= 2


def detect_memo_decorator(code: str) -> bool:
    return bool(re.search(
        r"@lru_cache|@cache|@memoize|\blru_cache\b|\bmemoize\b",
        code, re.IGNORECASE,
    ))


def count_comparisons(code: str) -> int:
    return len(re.findall(r"[<>]=?|==|!=", code))


# ══════════════════════════════════════════════════════════════
#  Syntax validation
# ══════════════════════════════════════════════════════════════

def check_syntax(code: str, lang: str) -> list:
    """
    Structural syntax checks.
    Returns a list of issue strings (empty = no issues found).
    Syntax errors appear inside 'issues' alongside algorithmic findings.
    """
    issues = []

    # ── Brace balance (Java / JS / C++) ──────────────────────
    if lang in ("java", "cpp", "javascript"):
        opens  = code.count("{")
        closes = code.count("}")
        if opens != closes:
            diff = abs(opens - closes)
            side = "closing '}'" if closes < opens else "opening '{'"
            issues.append(
                f"Syntax error: unmatched braces \u2014 {opens} '{{' vs {closes} '}}' "
                f"({diff} missing {side})."
            )

    # ── Parenthesis balance ───────────────────────────────────
    opens  = code.count("(")
    closes = code.count(")")
    if opens != closes:
        diff = abs(opens - closes)
        side = "closing ')'" if closes < opens else "opening '('"
        issues.append(
            f"Syntax error: unmatched parentheses \u2014 {opens} '(' vs {closes} ')' "
            f"({diff} missing {side})."
        )

    # ── Bracket balance ───────────────────────────────────────
    opens  = code.count("[")
    closes = code.count("]")
    if opens != closes:
        issues.append(
            f"Syntax error: unmatched brackets \u2014 {opens} '[' vs {closes} ']'."
        )

    # ── Missing semicolons (Java / C++ only) ──────────────────
    if lang in ("java", "cpp"):
        semi_count = 0
        for lineno, raw_line in enumerate(code.splitlines(), 1):
            line = raw_line.strip()
            if not line:
                continue
            # Skip lines that legitimately don't need semicolons
            if any([
                line.startswith(("//", "/*", "*", "#", "@")),
                line in ("{", "}"),
                line.endswith(("{", "}", ",")),
                re.match(
                    r"\b(if|else|for|while|do|switch|try|catch|finally"
                    r"|class|struct|namespace|public|private|protected)\b",
                    line,
                ),
            ]):
                continue
            if (
                not line.endswith(";")
                and len(line) > 4
                and re.search(r"[=\w\]]", line)
                and ("=" in line or "return" in line or "throw" in line)
                and not line.endswith("{")
            ):
                issues.append(
                    f"Syntax warning: line {lineno} may be missing semicolon \u2014 "
                    f"`{line[:70]}`"
                )
                semi_count += 1
                if semi_count >= 3:
                    issues.append("... (further semicolon warnings suppressed)")
                    break

    # ── Empty block bodies ────────────────────────────────────
    if re.search(r"\{\s*\}", code):
        issues.append(
            "Empty block body '{}' detected \u2014 may indicate incomplete code."
        )

    return issues


# ══════════════════════════════════════════════════════════════
#  Complexity estimation
# ══════════════════════════════════════════════════════════════

def estimate_complexity(
    loop_count:   int,
    loop_depth:   int,
    is_recursive: bool,
    has_halving:  bool,
) -> tuple:
    """
    Return (Big-O notation, notes_list).
    Same complexity tiers as complexity_analyzer.py (Python pipeline).
    """
    notes = []

    if is_recursive:
        notes.append("Recursive self-calls detected; exponential complexity assumed.")
        notes.append("Consider memoisation or an iterative rewrite.")
        return "O(2^n)", notes

    if loop_depth == 0:
        notes.append("No loops or recursion detected.")
        return "O(1)", notes

    if loop_depth == 1 and has_halving:
        notes.append("Single loop with halving step detected (binary-search pattern).")
        return "O(log n)", notes

    if loop_depth == 1:
        return "O(n)", notes

    if loop_depth == 2 and has_halving:
        notes.append("Outer linear loop with inner halving step detected.")
        return "O(n log n)", notes

    if loop_depth == 2:
        notes.append("Nested loops detected; consider algorithmic optimisation.")
        return "O(n^2)", notes

    if loop_depth == 3:
        notes.append("Triple-nested loops \u2014 high complexity; review algorithm.")
        return "O(n^3)", notes

    notes.append(f"{loop_depth}-level nested loops; very high complexity.")
    return f"O(n^{loop_depth})", notes


# ══════════════════════════════════════════════════════════════
#  Language-specific sort suggestions
# ══════════════════════════════════════════════════════════════

def sort_suggestion(lang: str) -> str:
    return {
        "python":     "Use Python's built-in sorted() or list.sort() (Timsort, O(n log n)).",
        "java":       "Use Arrays.sort() or Collections.sort() (dual-pivot / Timsort, O(n log n)).",
        "javascript": "Use Array.prototype.sort() (Timsort in V8, O(n log n)).",
        "cpp":        "Use std::sort() from <algorithm> (introsort, O(n log n)).",
    }.get(lang, "Use a built-in O(n log n) sort instead.")


# ══════════════════════════════════════════════════════════════
#  Algorithm pattern detection
#  Priority order mirrors pattern_detector.py _MATCHERS list
# ══════════════════════════════════════════════════════════════

def detect_pattern(
    code:         str,
    lang:         str,
    loop_count:   int,
    loop_depth:   int,
    is_recursive: bool,
    has_halving:  bool,
) -> tuple:
    """
    Returns (algorithm_name, pattern_desc, issues_list, suggestions_list).
    """
    comps     = count_comparisons(code)
    has_swap  = detect_swap(code)
    has_queue = detect_queue_usage(code)
    has_stack = detect_stack_usage(code)
    has_dp    = detect_dp_structure(code, loop_depth)
    has_memo  = detect_memo_decorator(code)

    # 1. DP Memoisation
    if has_memo:
        return (
            "Dynamic Programming \u2013 Memoisation",
            "top-down DP with cache decorator",
            [],
            ["Ensure cache is cleared between test runs if input changes."],
        )

    # 2. DP Tabulation
    if has_dp:
        return (
            "Dynamic Programming \u2013 Tabulation",
            "bottom-up DP with nested loop and table fill",
            ["Nested loops detected"],
            ["Verify base-case initialisation is correct."],
        )

    # 3. BFS
    if loop_count >= 1 and has_queue:
        return (
            "Breadth-First Search (BFS)",
            "iterative BFS with queue",
            [],
            ["Use a proper queue (ArrayDeque / deque) for O(1) dequeue."],
        )

    # 4. DFS Recursive
    if is_recursive:
        return (
            "Depth-First Search (DFS) \u2013 Recursive",
            "recursive DFS / tree traversal",
            ["Deep recursion may hit the call-stack limit."],
            ["Consider iterative DFS with an explicit stack for deep graphs."],
        )

    # 5. DFS Iterative
    if loop_count >= 1 and has_stack:
        return (
            "Depth-First Search (DFS) \u2013 Iterative",
            "iterative DFS with explicit stack",
            [],
            ["Ensure a visited set is maintained to avoid infinite loops."],
        )

    # 6. Binary Search
    if loop_count == 1 and has_halving and comps >= 1:
        return (
            "Binary Search",
            "iterative binary search with halving",
            [],
            ["Ensure the input array is sorted before calling binary search."],
        )

    # 7. Linear Search
    if loop_count == 1 and comps >= 1 and not has_halving:
        return (
            "Linear Search",
            "single-pass linear search",
            [],
            ["For repeated lookups, use a hash set/map for O(1) access."],
        )

    # 8. Bubble Sort (swap inside inner loop)
    if loop_depth >= 2 and comps > 0 and has_swap and detect_inner_loop_swap(code):
        return (
            "Bubble Sort",
            "comparison-based sorting \u2013 adjacent swap in inner loop",
            [
                "Nested loops detected \u2014 O(n\u00b2) time complexity.",
                "Swap performed inside inner loop.",
            ],
            [
                sort_suggestion(lang),
                "Add an 'early exit' flag to stop when no swaps occur in a pass.",
                "Nested loops detected; consider algorithmic optimisation.",
            ],
        )

    # 9. Selection Sort (swap outside inner loop)
    if loop_depth >= 2 and comps > 0 and has_swap:
        return (
            "Selection Sort",
            "comparison-based sorting \u2013 min/max selection",
            [
                "Nested loops detected \u2014 O(n\u00b2) time complexity.",
                "Swap performed after each inner-loop pass (min/max selection).",
            ],
            [sort_suggestion(lang)],
        )

    # 10. Insertion Sort
    if loop_depth >= 2 and comps > 0 and not has_swap:
        if re.search(r"\bj\s*-\s*1\b|\bshift\b", code, re.IGNORECASE):
            return (
                "Insertion Sort",
                "comparison-based sorting \u2013 shift and insert",
                ["Nested loops detected \u2014 O(n\u00b2) worst-case complexity."],
                [sort_suggestion(lang)],
            )

    # 11. Brute Force
    if loop_depth >= 2:
        return (
            "Brute Force",
            "exhaustive nested iteration",
            [
                f"{loop_depth}-level nested loops detected.",
                "High time complexity \u2014 may not scale with large input.",
            ],
            ["Profile with large inputs; consider divide-and-conquer or hashing."],
        )

    # 12. Single Pass
    if loop_count == 1:
        return ("Single-Pass Iteration", "linear traversal", [], [])

    # 13. Constant / no loops
    return ("Constant / Direct Computation", "no iteration", [], [])