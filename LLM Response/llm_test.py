"""
llm_test.py
-----------
Terminal tool — send a prompt to Groq and get JSON output.

Mimics exactly what Spring Boot sends:
  {
    "model": "llama-3.3-70b-versatile",
    "prompt": "You are a programming mentor...",
    "stream": false
  }

Setup:
    pip install groq
    $env:GROQ_API_KEY="gsk_..."     # Windows PowerShell
    export GROQ_API_KEY="gsk_..."   # Linux / Mac

Run:
    python llm_test.py
"""

import json
import os
import re
import sys
import time

# ── ANSI colours ──────────────────────────────────────────────
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7)
    except Exception:
        CYAN = GREEN = YELLOW = RED = BOLD = DIM = RESET = ""

SEP  = DIM  + "─" * 65 + RESET
SEP2 = BOLD + "═" * 65 + RESET

# ── Available Groq models ──────────────────────────────────────
GROQ_MODELS = [
    "llama-3.3-70b-versatile",        # best overall (default)
    "deepseek-r1-distill-llama-70b",  # best reasoning
    "llama3-70b-8192",                # reliable fallback
    "llama-3.1-8b-instant",           # fastest / lightweight
    "gemma2-9b-it",                   # Google Gemma
]
DEFAULT_MODEL = os.getenv("GROQ_MODEL", GROQ_MODELS[0])
GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")


# ══════════════════════════════════════════════════════════════
#  JSON extractor
# ══════════════════════════════════════════════════════════════

def extract_json(text: str) -> dict:
    """Extract JSON from LLM text — handles fences, preambles, trailing text."""
    # Strip markdown fences
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text.strip())
    text = re.sub(r"\n?```$",           "", text.strip())

    # Attempt 1: parse whole cleaned text
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Attempt 2: extract first { ... } block by brace counting
    start = text.find("{")
    if start != -1:
        depth, in_str, esc = 0, False, False
        for i, ch in enumerate(text[start:], start):
            if esc:               esc = False; continue
            if ch == "\\" and in_str: esc = True; continue
            if ch == '"':         in_str = not in_str; continue
            if in_str:            continue
            if   ch == "{":       depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break

    # Fallback
    return {
        "algorithm_detected":  "Unknown",
        "time_complexity":     "Unknown",
        "problem":             "LLM did not return valid JSON.",
        "explanation":         text,
        "suggested_algorithm": "",
        "improved_complexity": "",
        "improved_code":       "",
    }


# ══════════════════════════════════════════════════════════════
#  Groq caller
# ══════════════════════════════════════════════════════════════

def call_groq(model: str, prompt: str) -> dict:
    """Send prompt to Groq and return parsed JSON result."""
    try:
        from groq import Groq
    except ImportError:
        print(f"\n  {RED}groq package not installed.{RESET}")
        print(f"  Run:  {BOLD}pip install groq{RESET}\n")
        sys.exit(1)

    if not GROQ_API_KEY:
        print(f"\n  {RED}{BOLD}ERROR: GROQ_API_KEY is not set.{RESET}")
        print(f"  Get your free key at: {CYAN}https://console.groq.com{RESET}")
        print(f"\n  Set it in your terminal:")
        print(f"    {BOLD}Windows PowerShell :{RESET}  $env:GROQ_API_KEY=\"gsk_...\"")
        print(f"    {BOLD}Linux / Mac        :{RESET}  export GROQ_API_KEY=\"gsk_...\"\n")
        sys.exit(1)

    # ── Show the payload Spring Boot would send ────────────────
    payload = {"model": model, "prompt": prompt, "stream": False}
    print(f"\n{SEP}")
    print(f"{BOLD}  Payload (what Spring Boot sends):{RESET}")
    print(SEP)
    # Truncate long prompts for display
    display_payload = dict(payload)
    if len(prompt) > 300:
        display_payload["prompt"] = prompt[:300] + f"\n  ... [{len(prompt)-300} more chars]"
    print(json.dumps(display_payload, indent=2))
    print(SEP)
    print(f"\n  {DIM}Calling Groq API  model={model} ...{RESET}", flush=True)

    client = Groq(api_key=GROQ_API_KEY)
    start  = time.perf_counter()

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior software engineer and algorithm expert. "
                        "You MUST respond with ONLY a valid JSON object — "
                        "no markdown fences, no explanation outside the JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1024,
        )
    except Exception as exc:
        error_msg = str(exc)
        if "401" in error_msg or "invalid_api_key" in error_msg.lower():
            print(f"\n  {RED}{BOLD}ERROR: Invalid API key.{RESET}")
            print(f"  Check your key at: {CYAN}https://console.groq.com{RESET}\n")
        elif "model" in error_msg.lower():
            print(f"\n  {RED}{BOLD}ERROR: Model '{model}' not found.{RESET}")
            print(f"  Available models: {', '.join(GROQ_MODELS)}\n")
        else:
            print(f"\n  {RED}{BOLD}ERROR:{RESET} {exc}\n")
        sys.exit(1)

    elapsed = (time.perf_counter() - start) * 1_000
    text    = completion.choices[0].message.content or ""
    tokens  = completion.usage.completion_tokens if completion.usage else 0

    print(f"  {GREEN}Response received in {elapsed:.0f} ms  |  {tokens} tokens{RESET}")

    return {
        "raw_text":   text,
        "model":      completion.model,
        "eval_count": tokens,
        "elapsed_ms": round(elapsed, 2),
    }


# ══════════════════════════════════════════════════════════════
#  Input helpers
# ══════════════════════════════════════════════════════════════

def read_single(label: str, default: str = "") -> str:
    hint = f" {DIM}[{default}]{RESET}" if default else ""
    try:
        val = input(f"  {BOLD}{label}{RESET}{hint}: ").strip()
    except EOFError:
        return default
    return val if val else default


def read_multiline(label: str) -> str:
    print(f"\n  {BOLD}{label}{RESET}")
    print(f"  {DIM}Paste your content below. Type {BOLD}done{RESET}{DIM} on a new line to submit.{RESET}\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().lower() == "done":
            break
        lines.append(line)
    return "\n".join(lines).strip()


# ══════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════

def main():
    print(f"\n{CYAN}{BOLD}")
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║        LLM ENGINE  —  TERMINAL TESTER  (Groq)       ║")
    print("  ║    Simulates the Spring Boot → Groq API payload      ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print(f"{RESET}")

    # API key status
    if GROQ_API_KEY:
        masked = GROQ_API_KEY[:8] + "..." + GROQ_API_KEY[-4:]
        print(f"  API Key : {GREEN}{masked}{RESET}")
    else:
        print(f"  API Key : {RED}NOT SET — run will fail{RESET}")

    print(f"  Models  : {DIM}{', '.join(GROQ_MODELS)}{RESET}")
    print(f"  {DIM}Type 'exit' at any prompt to quit.{RESET}\n")

    while True:
        print(SEP)

        # ── 1. Choose model ───────────────────────────────────
        print(f"\n  {BOLD}Available models:{RESET}")
        for idx, m in enumerate(GROQ_MODELS, 1):
            tag = f"  {GREEN}← recommended{RESET}" if idx == 1 else ""
            print(f"    {DIM}{idx}.{RESET} {m}{tag}")

        model = read_single("Model name", DEFAULT_MODEL)
        if model.lower() == "exit":
            break

        # ── 2. Enter prompt ───────────────────────────────────
        prompt = read_multiline("Enter your prompt")
        if not prompt or prompt.lower() == "exit":
            if not prompt:
                print(f"  {YELLOW}No prompt entered. Try again.{RESET}\n")
            else:
                break
            continue

        # ── 3. Call Groq ──────────────────────────────────────
        response = call_groq(model, prompt)

        # ── 4. Parse LLM text → JSON ──────────────────────────
        result = extract_json(response["raw_text"])

        # ── 5. Print JSON output ──────────────────────────────
        print(f"\n{SEP2}")
        print(f"{BOLD}  LLM JSON Response:{RESET}")
        print(SEP2)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(SEP2)

        # ── 6. Metadata ───────────────────────────────────────
        print(f"\n  {DIM}Model      : {response['model']}")
        print(f"  Tokens     : {response['eval_count']}")
        print(f"  Elapsed    : {response['elapsed_ms']} ms{RESET}")

        # ── 7. Continue? ──────────────────────────────────────
        print(f"\n  {DIM}Press Enter to test again, or type 'exit' to quit:{RESET}")
        try:
            again = input().strip().lower()
        except EOFError:
            break
        if again == "exit":
            break
        print()

    print(f"\n{DIM}  Goodbye!{RESET}\n")


if __name__ == "__main__":
    main()