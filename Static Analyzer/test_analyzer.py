"""
test_analyzer.py
----------------
Comprehensive test suite for the static_analyzer package.

Run with:
    pytest test_analyzer.py -v
    pytest test_analyzer.py -v --cov=static_analyzer --cov-report=term-missing
"""

import sys
import os

# ── Make sure the package is importable when running from the project root ──
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from static_analyzer import analyze_code


# ══════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════

def is_success(result: dict) -> bool:
    return "error" not in result

def is_error(result: dict) -> bool:
    return "error" in result


# ══════════════════════════════════════════════════════════════
#  1. INPUT VALIDATION
# ══════════════════════════════════════════════════════════════

class TestInputValidation:

    def test_empty_string_returns_error(self):
        result = analyze_code("")
        assert is_error(result)
        assert "empty" in result["error"].lower()

    def test_whitespace_only_returns_error(self):
        result = analyze_code("   \n\t  ")
        assert is_error(result)

    def test_non_string_int_returns_error(self):
        result = analyze_code(42)
        assert is_error(result)
        assert "str" in result["error"].lower()

    def test_non_string_none_returns_error(self):
        result = analyze_code(None)
        assert is_error(result)

    def test_non_string_list_returns_error(self):
        result = analyze_code(["for i in range(10):", "    pass"])
        assert is_error(result)

    def test_oversized_input_returns_error(self):
        huge_code = "x = 1\n" * 20_000      # well over 50 000 chars
        result = analyze_code(huge_code)
        assert is_error(result)
        assert "exceed" in result["error"].lower()


# ══════════════════════════════════════════════════════════════
#  2. SYNTAX / PARSE ERRORS
# ══════════════════════════════════════════════════════════════

class TestParseErrors:

    def test_syntax_error_returns_error(self):
        result = analyze_code("def broken(: pass")
        assert is_error(result)
        assert "SyntaxError" in result["error"]

    def test_incomplete_function_returns_error(self):
        result = analyze_code("def foo(")
        assert is_error(result)

    def test_unmatched_bracket_returns_error(self):
        result = analyze_code("x = [1, 2, 3")
        assert is_error(result)

    def test_syntax_error_includes_line_details(self):
        result = analyze_code("def broken(: pass")
        assert is_error(result)
        # details dict should carry line info
        if "details" in result:
            assert result["details"].get("line") is not None


# ══════════════════════════════════════════════════════════════
#  3. RESPONSE SCHEMA
# ══════════════════════════════════════════════════════════════

class TestResponseSchema:

    REQUIRED_KEYS = {
        "algorithm_detected",
        "time_complexity",
        "issues",
        "loop_count",
        "pattern",
        "suggestions",
        "complexity_notes",
        "loop_depth",
        "is_recursive",
        "has_halving_pattern",
        "elapsed_ms",
    }

    def test_all_required_keys_present(self):
        result = analyze_code("x = 1 + 1")
        assert self.REQUIRED_KEYS.issubset(result.keys()), (
            f"Missing keys: {self.REQUIRED_KEYS - result.keys()}"
        )

    def test_issues_is_list(self):
        result = analyze_code("x = 1")
        assert isinstance(result["issues"], list)

    def test_suggestions_is_list(self):
        result = analyze_code("x = 1")
        assert isinstance(result["suggestions"], list)

    def test_loop_count_is_int(self):
        result = analyze_code("x = 1")
        assert isinstance(result["loop_count"], int)

    def test_elapsed_ms_is_float(self):
        result = analyze_code("x = 1")
        assert isinstance(result["elapsed_ms"], float)
        assert result["elapsed_ms"] >= 0

    def test_is_recursive_is_bool(self):
        result = analyze_code("x = 1")
        assert isinstance(result["is_recursive"], bool)


# ══════════════════════════════════════════════════════════════
#  4. COMPLEXITY DETECTION
# ══════════════════════════════════════════════════════════════

class TestComplexityDetection:

    def test_constant_complexity(self):
        result = analyze_code("x = 42\ny = x * 2")
        assert result["time_complexity"] == "O(1)"

    def test_single_loop_is_linear(self):
        result = analyze_code("""
for i in range(n):
    print(i)
""")
        assert result["time_complexity"] == "O(n)"

    def test_nested_two_loops_is_quadratic(self):
        result = analyze_code("""
for i in range(n):
    for j in range(n):
        print(i, j)
""")
        assert result["time_complexity"] == "O(n^2)"

    def test_triple_nested_loops_is_cubic(self):
        result = analyze_code("""
for i in range(n):
    for j in range(n):
        for k in range(n):
            print(i, j, k)
""")
        assert result["time_complexity"] == "O(n^3)"

    def test_binary_search_is_log_n(self):
        result = analyze_code("""
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
""")
        assert result["time_complexity"] == "O(log n)"

    def test_recursive_function_is_exponential(self):
        result = analyze_code("""
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
""")
        assert result["time_complexity"] == "O(2^n)"
        assert result["is_recursive"] is True

    def test_loop_depth_value(self):
        result = analyze_code("""
for i in range(n):
    for j in range(n):
        pass
""")
        assert result["loop_depth"] == 2

    def test_loop_count_matches(self):
        result = analyze_code("""
for i in range(5):
    pass
for j in range(5):
    pass
""")
        assert result["loop_count"] == 2


# ══════════════════════════════════════════════════════════════
#  5. PATTERN DETECTION
# ══════════════════════════════════════════════════════════════

class TestPatternDetection:

    def test_bubble_sort_detected(self):
        result = analyze_code("""
for i in range(len(arr)):
    for j in range(len(arr) - i - 1):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
""")
        assert result["algorithm_detected"] == "Bubble Sort"
        assert result["time_complexity"] == "O(n^2)"
        assert result["loop_count"] == 2

    def test_binary_search_detected(self):
        result = analyze_code("""
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
""")
        assert result["algorithm_detected"] == "Binary Search"

    def test_linear_search_detected(self):
        result = analyze_code("""
def linear_search(arr, val):
    for i, x in enumerate(arr):
        if x == val:
            return i
    return -1
""")
        assert result["algorithm_detected"] == "Linear Search"
        assert result["time_complexity"] == "O(n)"

    def test_dfs_recursive_detected(self):
        result = analyze_code("""
def dfs(node, visited):
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(neighbor, visited)
""")
        assert "DFS" in result["algorithm_detected"]
        assert result["is_recursive"] is True

    def test_dp_tabulation_detected(self):
        result = analyze_code("""
def lcs(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[len(a)][len(b)]
""")
        assert "Dynamic Programming" in result["algorithm_detected"]
        assert "Tabulation" in result["algorithm_detected"]

    def test_dp_memoisation_with_decorator(self):
        result = analyze_code("""
import functools

@functools.lru_cache(maxsize=None)
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
""")
        assert "Memoisation" in result["algorithm_detected"]

    def test_constant_pattern_detected(self):
        result = analyze_code("result = 2 ** 10")
        assert result["algorithm_detected"] == "Constant / Direct Computation"
        assert result["time_complexity"] == "O(1)"
        assert result["loop_count"] == 0

    def test_single_pass_detected(self):
        result = analyze_code("""
total = 0
for x in numbers:
    total += x
""")
        assert result["algorithm_detected"] == "Single-Pass Iteration"
        assert result["loop_count"] == 1


# ══════════════════════════════════════════════════════════════
#  6. ISSUES & SUGGESTIONS CONTENT
# ══════════════════════════════════════════════════════════════

class TestIssuesAndSuggestions:

    def test_bubble_sort_has_nested_loop_issue(self):
        result = analyze_code("""
for i in range(len(arr)):
    for j in range(len(arr) - i - 1):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
""")
        issues_text = " ".join(result["issues"]).lower()
        assert "nested" in issues_text or "loop" in issues_text

    def test_bubble_sort_suggests_builtin_sort(self):
        result = analyze_code("""
for i in range(len(arr)):
    for j in range(len(arr) - i - 1):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
""")
        suggestions_text = " ".join(result["suggestions"]).lower()
        assert "sort" in suggestions_text or "timsort" in suggestions_text

    def test_recursive_fib_suggests_memoisation(self):
        result = analyze_code("""
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
""")
        suggestions_text = " ".join(result["suggestions"]).lower()
        assert "memo" in suggestions_text or "cache" in suggestions_text or "iterative" in suggestions_text

    def test_binary_search_suggests_sorted(self):
        result = analyze_code("""
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
""")
        suggestions_text = " ".join(result["suggestions"]).lower()
        assert "sorted" in suggestions_text

    def test_clean_code_has_no_issues(self):
        result = analyze_code("x = sum(range(100))")
        assert result["issues"] == []


# ══════════════════════════════════════════════════════════════
#  7. EDGE CASES
# ══════════════════════════════════════════════════════════════

class TestEdgeCases:

    def test_single_line_function(self):
        result = analyze_code("def add(a, b): return a + b")
        assert is_success(result)
        assert result["time_complexity"] == "O(1)"

    def test_class_definition(self):
        result = analyze_code("""
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None
""")
        assert is_success(result)

    def test_list_comprehension_no_loop_nodes(self):
        result = analyze_code("squares = [x**2 for x in range(10)]")
        assert is_success(result)

    def test_multiline_valid_code(self):
        result = analyze_code("""
def selection_sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
""")
        assert is_success(result)
        assert result["loop_count"] == 2

    def test_while_loop_counts_as_loop(self):
        result = analyze_code("""
i = 0
while i < n:
    i += 1
""")
        assert result["loop_count"] == 1
        assert result["time_complexity"] == "O(n)"

    def test_code_with_only_comments(self):
        # Comments alone are valid Python
        result = analyze_code("# This is just a comment\n# Nothing here")
        assert is_success(result)
        assert result["time_complexity"] == "O(1)"

    def test_unicode_identifiers(self):
        result = analyze_code("résultat = 42")
        assert is_success(result)

    def test_returns_dict(self):
        result = analyze_code("pass")
        assert isinstance(result, dict)


# ══════════════════════════════════════════════════════════════
#  8. FULL INTEGRATION — exact output snapshot
# ══════════════════════════════════════════════════════════════

class TestIntegrationSnapshot:
    """
    Verifies the complete output dict for the canonical Bubble Sort example
    from the original project specification.
    """

    CODE = """
for i in range(len(arr)):
    for j in range(len(arr)):
        if arr[i] > arr[j]:
            arr[i], arr[j] = arr[j], arr[i]
"""

    def test_snapshot_algorithm_detected(self):
        assert analyze_code(self.CODE)["algorithm_detected"] == "Bubble Sort"

    def test_snapshot_time_complexity(self):
        assert analyze_code(self.CODE)["time_complexity"] == "O(n^2)"

    def test_snapshot_loop_count(self):
        assert analyze_code(self.CODE)["loop_count"] == 2

    def test_snapshot_pattern(self):
        pattern = analyze_code(self.CODE)["pattern"].lower()
        assert "sort" in pattern or "comparison" in pattern

    def test_snapshot_has_issues(self):
        assert len(analyze_code(self.CODE)["issues"]) > 0

    def test_snapshot_not_recursive(self):
        assert analyze_code(self.CODE)["is_recursive"] is False

    def test_snapshot_no_halving(self):
        assert analyze_code(self.CODE)["has_halving_pattern"] is False