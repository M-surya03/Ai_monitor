"""
llm_engine
----------
LLM analysis engine powered by Groq API.

Quick start::

    from llm_engine import run_llm_analysis, check_groq_health

    health = check_groq_health()
    result = run_llm_analysis(source_code, static_analyzer_result)
"""

from .engine import check_groq_health, run_llm_analysis

# backwards compat alias
check_ollama_health = check_groq_health

__all__ = ["run_llm_analysis", "check_groq_health"]
__version__ = "2.0.0"