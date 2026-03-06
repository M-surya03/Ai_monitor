"""
pattern_detector.py
--------------------
Identifies common algorithm patterns from an AST.

Supported detections
--------------------
Sorting algorithms:
    Bubble Sort      – nested loops + adjacent swap
    Selection Sort   – nested loops + min-index tracking + single swap
    Insertion Sort   – nested loops + shift/insert pattern

Search algorithms:
    Binary Search    – single loop + halving + comparison
    Linear Search    – single loop + comparison + early return/break

Graph / tree traversal:
    BFS              – queue (deque/list) + while loop + extend/append
    DFS (iterative)  – stack (list) + while/for loop + append/pop
    DFS (recursive)  – recursive function + list/dict traversal

Dynamic Programming:
    Memoisation      – lru_cache decorator or manual dict cache
    Tabulation       – 2-D list construction inside nested loop

General fallback:
    Brute Force      – nested loops without recognised pattern
    Single Pass      – one loop, no nesting
    Constant         – no loops, no recursion
"""

import ast
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Small AST helper utilities
# ──────────────────────────────────────────────────────────────

def _count_loops(tree: ast.AST) -> int:
    return sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While)))


def _count_comparisons(tree: ast.AST) -> int:
    return sum(1 for n in ast.walk(tree) if isinstance(n, ast.Compare))


def _has_swap(tree: ast.AST) -> bool:
    """Detect tuple-swap: a, b = b, a  or  arr[i], arr[j] = arr[j], arr[i]"""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Tuple)
            and isinstance(node.value, ast.Tuple)
            and len(node.targets[0].elts) == len(node.value.elts) == 2
        ):
            return True
    return False


def _has_halving(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.AugAssign) and isinstance(node.op, (ast.FloorDiv, ast.RShift)):
            return True
        if isinstance(node, ast.Assign):
            for child in ast.walk(node.value):
                if isinstance(child, ast.BinOp) and isinstance(child.op, (ast.FloorDiv, ast.RShift)):
                    return True
    return False


def _has_early_exit(tree: ast.AST) -> bool:
    return any(isinstance(n, (ast.Return, ast.Break)) for n in ast.walk(tree))


def _function_names(tree: ast.AST) -> list[str]:
    return [
        n.func.id if isinstance(n.func, ast.Name) else
        n.func.attr if isinstance(n.func, ast.Attribute) else ""
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
    ]


def _decorator_names(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    names.append(dec.id)
                elif isinstance(dec, ast.Attribute):
                    names.append(dec.attr)
    return names


def _has_2d_list_init_in_nested_loop(tree: ast.AST) -> bool:
    """
    Heuristic: a subscript target (e.g. dp[i][j] = ...) inside a nested
    loop strongly suggests tabulation DP.
    Also matches explicit list/dict construction in nested loops.
    """
    for outer in ast.walk(tree):
        if not isinstance(outer, (ast.For, ast.While)):
            continue
        for inner in ast.walk(outer):
            if inner is outer:
                continue
            if isinstance(inner, (ast.For, ast.While)):
                for assign in ast.walk(inner):
                    if isinstance(assign, ast.Assign):
                        # Target is a subscript → filling a table cell
                        for target in assign.targets:
                            if isinstance(target, ast.Subscript):
                                return True
                        # RHS is a list/dict literal construction
                        if isinstance(assign.value, (ast.List, ast.Dict)):
                            return True
    return False


def _is_recursive(tree: ast.AST) -> bool:
    for func_def in ast.walk(tree):
        if not isinstance(func_def, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        name = func_def.name
        if sum(
            1
            for n in ast.walk(func_def)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Name)
            and n.func.id == name
        ) >= 1:
            return True
    return False


def _uses_deque_or_queue(tree: ast.AST) -> bool:
    calls = _function_names(tree)
    imports = [
        alias.name
        for n in ast.walk(tree)
        if isinstance(n, ast.Import)
        for alias in n.names
    ] + [
        n.module or ""
        for n in ast.walk(tree)
        if isinstance(n, ast.ImportFrom)
    ]
    return "deque" in calls or "Queue" in calls or "deque" in " ".join(imports)


# ──────────────────────────────────────────────────────────────
# Pattern matchers  (ordered from most specific → least specific)
# ──────────────────────────────────────────────────────────────

@dataclass
class PatternResult:
    algorithm: str
    pattern: str
    loop_count: int
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "pattern": self.pattern,
            "loop_count": self.loop_count,
            "issues": self.issues,
            "suggestions": self.suggestions,
        }


# Each matcher returns a PatternResult or None (if it doesn't match).
_MATCHERS: list  # defined below after all functions


def _match_dp_memo(tree: ast.AST, loops: int, _comps: int) -> Optional[PatternResult]:
    decs = _decorator_names(tree)
    calls = _function_names(tree)
    if "lru_cache" in decs or "cache" in decs or "memoize" in decs:
        return PatternResult(
            algorithm="Dynamic Programming – Memoisation",
            pattern="top-down DP with cache decorator",
            loop_count=loops,
            suggestions=["Ensure cache is cleared between test runs if input data changes."],
        )
    # Manual dict cache heuristic
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body_src = ast.dump(node)
            if "memo" in body_src.lower() or "cache" in body_src.lower() or "dp" in body_src.lower():
                if _is_recursive(tree):
                    return PatternResult(
                        algorithm="Dynamic Programming – Memoisation",
                        pattern="top-down DP with manual cache dict",
                        loop_count=loops,
                        suggestions=["Consider @functools.lru_cache for cleaner memoisation."],
                    )
    return None


def _match_dp_tabulation(tree: ast.AST, loops: int, _comps: int) -> Optional[PatternResult]:
    if loops >= 2 and _has_2d_list_init_in_nested_loop(tree):
        return PatternResult(
            algorithm="Dynamic Programming – Tabulation",
            pattern="bottom-up DP with nested loop and table fill",
            loop_count=loops,
            issues=["Nested loops detected"],
            suggestions=["Verify base-case initialisation is correct."],
        )
    return None


def _match_bfs(tree: ast.AST, loops: int, _comps: int) -> Optional[PatternResult]:
    calls = _function_names(tree)
    has_queue = _uses_deque_or_queue(tree)
    has_extend = "extend" in calls or "append" in calls
    if loops >= 1 and (has_queue or has_extend):
        # BFS uses a queue and typically popleft / pop(0)
        if "popleft" in calls or any(
            isinstance(n, ast.Subscript) for n in ast.walk(tree)
        ):
            if has_queue:
                return PatternResult(
                    algorithm="Breadth-First Search (BFS)",
                    pattern="iterative BFS with queue",
                    loop_count=loops,
                    suggestions=["Use collections.deque for O(1) popleft."],
                )
    return None


def _match_dfs_recursive(tree: ast.AST, loops: int, _comps: int) -> Optional[PatternResult]:
    if _is_recursive(tree):
        return PatternResult(
            algorithm="Depth-First Search (DFS) – Recursive",
            pattern="recursive DFS / tree traversal",
            loop_count=loops,
            issues=["Deep recursion may hit Python's default recursion limit (1 000)."],
            suggestions=["Add sys.setrecursionlimit() or convert to iterative DFS for deep trees."],
        )
    return None


def _match_dfs_iterative(tree: ast.AST, loops: int, _comps: int) -> Optional[PatternResult]:
    calls = _function_names(tree)
    if loops >= 1 and "append" in calls and "pop" in calls:
        return PatternResult(
            algorithm="Depth-First Search (DFS) – Iterative",
            pattern="iterative DFS with explicit stack",
            loop_count=loops,
            suggestions=["Ensure visited set is maintained to avoid infinite loops on cyclic graphs."],
        )
    return None


def _match_binary_search(tree: ast.AST, loops: int, comps: int) -> Optional[PatternResult]:
    if loops == 1 and comps >= 1 and _has_halving(tree) and _has_early_exit(tree):
        return PatternResult(
            algorithm="Binary Search",
            pattern="iterative binary search with halving",
            loop_count=loops,
            suggestions=["Ensure the input array is sorted before calling binary search."],
        )
    return None


def _match_linear_search(tree: ast.AST, loops: int, comps: int) -> Optional[PatternResult]:
    if loops == 1 and comps >= 1 and _has_early_exit(tree) and not _has_halving(tree):
        return PatternResult(
            algorithm="Linear Search",
            pattern="single-pass linear search",
            loop_count=loops,
            suggestions=["For repeated lookups, consider converting to a set/dict for O(1) access."],
        )
    return None


def _match_bubble_sort(tree: ast.AST, loops: int, comps: int) -> Optional[PatternResult]:
    if loops >= 2 and comps > 0 and _has_swap(tree):
        # Selection sort also has a swap; distinguish by inner loop structure.
        # Bubble sort: swap inside inner loop.
        # Selection sort: swap outside inner loop (min-index pattern).
        # Heuristic: if swap is inside the innermost loop body → bubble.
        for outer in ast.walk(tree):
            if not isinstance(outer, (ast.For, ast.While)):
                continue
            for inner in ast.walk(outer):
                if inner is outer:
                    continue
                if isinstance(inner, (ast.For, ast.While)):
                    if _has_swap(inner):
                        return PatternResult(
                            algorithm="Bubble Sort",
                            pattern="comparison-based sorting – adjacent swap in inner loop",
                            loop_count=loops,
                            issues=[
                                "Nested loops detected — O(n²) time complexity.",
                                "Swap performed inside inner loop.",
                            ],
                            suggestions=[
                                "Use Python's built-in sorted() or list.sort() (Timsort, O(n log n)).",
                                "Add an 'early exit' flag to stop when no swaps occur in a pass.",
                            ],
                        )
    return None


def _match_selection_sort(tree: ast.AST, loops: int, comps: int) -> Optional[PatternResult]:
    if loops >= 2 and comps > 0 and _has_swap(tree):
        return PatternResult(
            algorithm="Selection Sort",
            pattern="comparison-based sorting – min/max selection",
            loop_count=loops,
            issues=[
                "Nested loops detected — O(n²) time complexity.",
                "Performs a swap after each inner-loop pass.",
            ],
            suggestions=[
                "Use Python's built-in sorted() or list.sort() (Timsort, O(n log n)).",
            ],
        )
    return None


def _match_insertion_sort(tree: ast.AST, loops: int, comps: int) -> Optional[PatternResult]:
    # Insertion sort: nested loop + comparison + shift (augmented assignment or subscript assign)
    if loops >= 2 and comps > 0:
        has_shift = any(
            isinstance(n, (ast.AugAssign, ast.Assign))
            and isinstance(getattr(n, "targets", [None])[0] if hasattr(n, "targets") else None, ast.Subscript)
            for n in ast.walk(tree)
        )
        if has_shift and not _has_swap(tree):
            return PatternResult(
                algorithm="Insertion Sort",
                pattern="comparison-based sorting – shift and insert",
                loop_count=loops,
                issues=["Nested loops detected — O(n²) worst-case time complexity."],
                suggestions=["Use Python's built-in sorted() or bisect module for sorted insertion."],
            )
    return None


def _match_brute_force(tree: ast.AST, loops: int, comps: int) -> Optional[PatternResult]:
    if loops >= 2:
        return PatternResult(
            algorithm="Brute Force",
            pattern="exhaustive nested iteration",
            loop_count=loops,
            issues=[
                f"{loops}-level nested loop detected.",
                "High time complexity — may not scale.",
            ],
            suggestions=["Profile with large inputs. Consider divide-and-conquer or hashing."],
        )
    return None


def _match_single_pass(tree: ast.AST, loops: int, _comps: int) -> Optional[PatternResult]:
    if loops == 1:
        return PatternResult(
            algorithm="Single-Pass Iteration",
            pattern="linear traversal",
            loop_count=loops,
        )
    return None


def _match_constant(_tree: ast.AST, loops: int, _comps: int) -> Optional[PatternResult]:
    return PatternResult(
        algorithm="Constant / Direct Computation",
        pattern="no iteration",
        loop_count=0,
    )


_MATCHERS = [
    _match_dp_memo,
    _match_dp_tabulation,
    _match_bfs,
    _match_dfs_recursive,
    _match_dfs_iterative,
    _match_binary_search,
    _match_linear_search,
    _match_bubble_sort,
    _match_selection_sort,
    _match_insertion_sort,
    _match_brute_force,
    _match_single_pass,
    _match_constant,
]


# ──────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────

def detect_pattern(tree: ast.AST) -> PatternResult:
    """
    Identify the dominant algorithm pattern in *tree*.

    Args:
        tree: A parsed ``ast.AST`` object.

    Returns:
        :class:`PatternResult` with algorithm name, pattern description,
        loop count, issues, and improvement suggestions.
    """
    try:
        loops = _count_loops(tree)
        comps = _count_comparisons(tree)
    except Exception:  # noqa: BLE001
        logger.exception("Error collecting loop/comparison counts.")
        return PatternResult(
            algorithm="Unknown",
            pattern="analysis error",
            loop_count=0,
            issues=["Internal error during pattern detection."],
        )

    for matcher in _MATCHERS:
        try:
            result = matcher(tree, loops, comps)
            if result is not None:
                logger.debug("Pattern matched by %s: %s", matcher.__name__, result.algorithm)
                return result
        except Exception:  # noqa: BLE001
            logger.exception("Matcher %s raised an exception; skipping.", matcher.__name__)

    # Should never reach here (last matcher always returns a result).
    return PatternResult(
        algorithm="Unknown",
        pattern="unrecognised",
        loop_count=loops,
        issues=["Pattern could not be determined."],
    )
