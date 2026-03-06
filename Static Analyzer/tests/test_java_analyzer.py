import pytest
from static_analyzer import analyze_code


def test_java_single_loop():
    code = """
public class Test {
    public static void main(String[] args) {
        for(int i=0;i<n;i++){
            System.out.println(i);
        }
    }
}
"""
    result = analyze_code(code, language="java")

    assert result["loop_count"] == 1
    assert result["time_complexity"] == "O(n)"


def test_java_nested_loop():
    code = """
public class Test {
    public static void main(String[] args) {
        for(int i=0;i<n;i++){
            for(int j=0;j<n;j++){
                System.out.println(i + j);
            }
        }
    }
}
"""
    result = analyze_code(code, language="java")

    assert result["loop_depth"] == 2
    assert result["time_complexity"] == "O(n^2)"