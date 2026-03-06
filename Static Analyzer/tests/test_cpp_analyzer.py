import pytest
from static_analyzer import analyze_code


def test_cpp_single_loop():
    code = """
#include <iostream>
using namespace std;

int main() {
    for(int i=0;i<n;i++){
        cout << i;
    }
}
"""
    result = analyze_code(code, language="cpp")

    assert result["loop_count"] == 1
    assert result["time_complexity"] == "O(n)"


def test_cpp_nested_loop():
    code = """
#include <iostream>
using namespace std;

int main() {
    for(int i=0;i<n;i++){
        for(int j=0;j<n;j++){
            cout << i+j;
        }
    }
}
"""
    result = analyze_code(code, language="cpp")

    assert result["loop_depth"] == 2
    assert result["time_complexity"] == "O(n^2)"