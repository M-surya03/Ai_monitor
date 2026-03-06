import pytest
from static_analyzer import analyze_code


def test_js_single_loop():
    code = """
for (let i = 0; i < n; i++) {
    console.log(i);
}
"""
    result = analyze_code(code, language="javascript")

    assert result["loop_count"] == 1
    assert result["time_complexity"] == "O(n)"


def test_js_nested_loop():
    code = """
for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
        console.log(i,j);
    }
}
"""
    result = analyze_code(code, language="javascript")

    assert result["loop_depth"] == 2
    assert result["time_complexity"] == "O(n^2)"