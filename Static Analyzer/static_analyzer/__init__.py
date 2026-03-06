"""
static_analyzer
---------------
Multi-language static analysis package.

Supported languages: Python, Java, JavaScript / TypeScript, C++

Quick start::

    from static_analyzer import analyze_code

    # Auto-detect language
    result = analyze_code(source)

    # Explicit language
    result = analyze_code(source, language="java")
"""

from .analyzer import analyze_code

__all__ = ["analyze_code"]
__version__ = "2.0.0"