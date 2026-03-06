"""
config.py
---------
Central configuration for the LLM engine — powered by Groq API.

Environment variables
---------------------
GROQ_API_KEY    – your Groq API key  (required)
GROQ_MODEL      – model name         (default: llama-3.3-70b-versatile)
GROQ_TIMEOUT    – request timeout s  (default: 60)
GROQ_RETRIES    – max retry attempts (default: 3)
GROQ_TEMP       – temperature 0-1    (default: 0.2)

Get your free API key at: https://console.groq.com
"""

import os

# ── Groq API ───────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ── Best model for code analysis on Groq ──────────────────────
# llama-3.3-70b-versatile       → best overall accuracy + speed
# deepseek-r1-distill-llama-70b → best reasoning & explanation
# llama3-70b-8192               → reliable fallback
MODEL_NAME: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# ── Request settings ───────────────────────────────────────────
TIMEOUT: int     = int(os.getenv("GROQ_TIMEOUT", "60"))
MAX_RETRIES: int = int(os.getenv("GROQ_RETRIES", "3"))

# ── Generation settings ────────────────────────────────────────
TEMPERATURE: float = float(os.getenv("GROQ_TEMP", "0.2"))
MAX_TOKENS: int    = 1024