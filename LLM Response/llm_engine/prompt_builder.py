"""
prompt_builder.py
-----------------
Builds the LLM prompt from source code + static analysis result.

Design goals
------------
- The prompt is strict: it tells the model to return ONLY JSON.
- It includes a concrete schema so the model knows the exact shape.
- It embeds the static analysis result so the model can validate
  or correct the heuristic findings.
- Temperature is kept low (see config.py) to reduce hallucination.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Schema embedded in the prompt ──────────────────────────────
_RESPONSE_SCHEMA = """\
{
  "algorithm_detected":  "<exact algorithm name>",
  "time_complexity":     "<Big-O notation>",
  "space_complexity":    "<Big-O notation>",
  "problem":             "<one-sentence description of the main issue>",
  "explanation":         "<clear paragraph explaining the algorithm>",
  "suggested_algorithm": "<name of a better algorithm, or 'None'>",
  "improved_complexity": "<Big-O of the suggested algorithm>",
  "improved_code":       "<complete, runnable Python code as a string>",
  "key_improvements":    ["<improvement 1>", "<improvement 2>"]
}"""

_PROMPT_TEMPLATE = """\
You are a senior software engineer and algorithm expert acting as a code reviewer.

Your task is to analyse the Python code below and return a structured JSON report.

═══════════════════════════════════════
SOURCE CODE
═══════════════════════════════════════
{code}

═══════════════════════════════════════
STATIC ANALYSIS (pre-computed hints)
═══════════════════════════════════════
Algorithm guess  : {algorithm_detected}
Time complexity  : {time_complexity}
Detected issues  : {issues}
Loop depth       : {loop_depth}
Is recursive     : {is_recursive}

═══════════════════════════════════════
YOUR TASKS
═══════════════════════════════════════
1. Confirm or correct the algorithm name.
2. Confirm or correct the time complexity.
3. Estimate space complexity.
4. Describe the main problem with this implementation.
5. Explain clearly how the algorithm works.
6. Suggest a better algorithm if one exists.
7. State the improved time complexity.
8. Write complete, runnable optimized Python code.
9. List 2-4 key improvements made.

═══════════════════════════════════════
OUTPUT RULES  ← READ CAREFULLY
═══════════════════════════════════════
- Return ONLY the JSON object below. No preamble, no explanation outside JSON.
- Do NOT wrap the JSON in markdown code fences (no ```).
- All string values must be valid JSON strings (escape newlines as \\n).
- The "improved_code" field must be a complete Python function as a single string.

RESPONSE SCHEMA:
{schema}
"""


def build_prompt(code: str, static_result: dict[str, Any]) -> str:
    """
    Build a structured LLM prompt.

    Args:
        code:          Raw Python source code submitted by the user.
        static_result: Output dict from ``static_analyzer.analyze_code()``.

    Returns:
        A fully formatted prompt string ready to send to the LLM.

    Raises:
        ValueError: If ``code`` is empty or ``static_result`` is missing
                    required keys.
    """
    if not code or not code.strip():
        raise ValueError("build_prompt: code must not be empty.")

    required = {"algorithm_detected", "time_complexity", "issues"}
    missing = required - static_result.keys()
    if missing:
        raise ValueError(f"build_prompt: static_result missing keys: {missing}")

    issues_fmt = (
        "\n  - " + "\n  - ".join(static_result["issues"])
        if static_result.get("issues")
        else "None"
    )

    prompt = _PROMPT_TEMPLATE.format(
        code=code.strip(),
        algorithm_detected=static_result.get("algorithm_detected", "Unknown"),
        time_complexity=static_result.get("time_complexity", "Unknown"),
        issues=issues_fmt,
        loop_depth=static_result.get("loop_depth", "N/A"),
        is_recursive=static_result.get("is_recursive", False),
        schema=_RESPONSE_SCHEMA,
    )

    logger.debug(
        "Prompt built — model=%s code_len=%d",
        "deepseek-coder",
        len(code),
    )
    return prompt