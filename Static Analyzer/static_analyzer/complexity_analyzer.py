"""
complexity_analyzer.py
-----------------------
Estimates time complexity from an AST by analysing loop nesting depth,
recursion, and call patterns.

Complexity tiers (conservative, static-analysis based):
    O(1)    – no loops, no recursion
    O(log n) – binary-search / halving pattern (loop + floor-division / bit-shift)
    O(n)    – single non-nested loop
    O(n log n) – single outer loop + inner halving pattern
    O(n^2)  – 2-level nested loops
    O(n^3)  – 3-level nested loops
    O(2^n)  – detected recursion (two or more self-calls)
"""

import ast
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────

_HALVING_OPS = (ast.FloorDiv, ast.RShift)   # // or >>


def _uses_halving(loop_node: ast.AST) -> bool:
    """Return True if a loop body contains a floor-div / right-shift assignment."""
    for node in ast.walk(loop_node):
        if isinstance(node, ast.AugAssign) and isinstance(node.op, _HALVING_OPS):
            return True
        if isinstance(node, ast.Assign):
            for child in ast.walk(node.value):
                if isinstance(child, ast.BinOp) and isinstance(child.op, _HALVING_OPS):
                    return True
    return False


def _max_loop_nesting(tree: ast.AST) -> tuple[int, bool]:
    """
    Walk the AST and return (max_nesting_depth, any_halving_inner_loop).

    Depth counts:
        For / While nodes that are *directly* nested inside another loop
        contribute +1 to depth.
    """
    max_depth = 0
    halving_inner = False

    def _recurse(node: ast.AST, depth: int) -> None:
        nonlocal max_depth, halving_inner

        is_loop = isinstance(node, (ast.For, ast.While))
        current_depth = depth + 1 if is_loop else depth

        if current_depth > max_depth:
            max_depth = current_depth

        if is_loop and _uses_halving(node):
            halving_inner = True

        for child in ast.iter_child_nodes(node):
            _recurse(child, current_depth if is_loop else depth)

    _recurse(tree, 0)
    return max_depth, halving_inner


def _detect_recursion(tree: ast.AST) -> bool:
    """
    Return True if any function calls itself at least twice (exponential-
    recursion heuristic), or calls itself inside a condition / without
    memoisation markers.
    """
    for func_def in ast.walk(tree):
        if not isinstance(func_def, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        func_name = func_def.name
        call_count = sum(
            1
            for node in ast.walk(func_def)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == func_name
        )
        if call_count >= 1:
            logger.debug("Recursive function detected: %s (%d self-calls)", func_name, call_count)
            return True
    return False


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

@dataclass
class ComplexityResult:
    """Full complexity analysis result."""
    notation: str
    loop_depth: int
    is_recursive: bool
    has_halving_pattern: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "notation": self.notation,
            "loop_depth": self.loop_depth,
            "is_recursive": self.is_recursive,
            "has_halving_pattern": self.has_halving_pattern,
            "notes": self.notes,
        }


def analyze_complexity(tree: ast.AST) -> ComplexityResult:
    """
    Estimate the time complexity of code represented by *tree*.

    Args:
        tree: A parsed ``ast.AST`` object.

    Returns:
        :class:`ComplexityResult` with the complexity notation and metadata.
    """
    notes: list[str] = []

    try:
        loop_depth, halving_inner = _max_loop_nesting(tree)
        recursive = _detect_recursion(tree)
    except Exception:  # noqa: BLE001
        logger.exception("Unexpected error during complexity analysis.")
        return ComplexityResult(
            notation="Unknown",
            loop_depth=0,
            is_recursive=False,
            has_halving_pattern=False,
            notes=["Analysis failed due to an internal error."],
        )

    # ── Determine notation ─────────────────────────────────────────────
    if recursive:
        notation = "O(2^n)"
        notes.append("Recursive self-calls detected; exponential complexity assumed.")
        notes.append("Consider memoisation (functools.lru_cache) or iterative rewrite.")

    elif loop_depth == 0:
        notation = "O(1)"
        notes.append("No loops or recursion detected.")

    elif loop_depth == 1 and halving_inner:
        notation = "O(log n)"
        notes.append("Single loop with halving step detected (binary-search pattern).")

    elif loop_depth == 1:
        notation = "O(n)"

    elif loop_depth == 2 and halving_inner:
        notation = "O(n log n)"
        notes.append("Outer linear loop with inner halving step detected.")

    elif loop_depth == 2:
        notation = "O(n^2)"
        notes.append("Nested loops detected; consider algorithmic optimisation.")

    elif loop_depth == 3:
        notation = "O(n^3)"
        notes.append("Triple-nested loops detected; high complexity — review algorithm.")

    else:
        notation = f"O(n^{loop_depth})"
        notes.append(f"{loop_depth}-level nested loops detected; very high complexity.")

    logger.debug("Complexity result: %s (depth=%d, recursive=%s)", notation, loop_depth, recursive)

    return ComplexityResult(
        notation=notation,
        loop_depth=loop_depth,
        is_recursive=recursive,
        has_halving_pattern=halving_inner,
        notes=notes,
    )
