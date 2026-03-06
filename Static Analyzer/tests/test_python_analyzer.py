import pytest
from static_analyzer import analyze_code


def test_python_constant_complexity():
    code = """
x = 5
y = x * 2
"""
    result = analyze_code(code, language="python")

    assert result["time_complexity"] == "O(1)"
    assert result["loop_count"] == 0


def test_python_single_loop():
    code = """
for i in range(n):
    print(i)
"""
    result = analyze_code(code, language="python")

    assert result["time_complexity"] == "O(n)"
    assert result["loop_count"] == 1


def test_python_nested_loop():
    code = """
for i in range(n):
    for j in range(n):
        print(i,j)
"""
    result = analyze_code(code, language="python")

    assert result["time_complexity"] == "O(n^2)"
    assert result["loop_depth"] == 2


def test_python_recursion():
    code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
"""
    result = analyze_code(code, language="python")

    assert result["is_recursive"] is True