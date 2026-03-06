"""
run.py  —  Multi-Language Static Analyzer CLI  v2.0

Usage:
    python run.py                         # interactive (auto-detect language)
    python run.py mycode.py               # analyze file
    python run.py mycode.java  --java     # explicit language
    python run.py mycode.js    --js
    python run.py mycode.cpp   --cpp
    cat mycode.py | python run.py         # pipe mode
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from static_analyzer import analyze_code

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

SEP = DIM + "─" * 64 + RESET

LANG_BADGE = {
    "python":     f"\033[93m[PYTHON]\033[0m",
    "java":       f"\033[91m[JAVA]\033[0m",
    "javascript": f"\033[92m[JAVASCRIPT]\033[0m",
    "cpp":        f"\033[96m[C++]\033[0m",
    "unknown":    f"{DIM}[UNKNOWN]{RESET}",
}

FLAG_MAP = {
    "--python":     "python",
    "--java":       "java",
    "--js":         "javascript",
    "--javascript": "javascript",
    "--cpp":        "cpp",
    "--c++":        "cpp",
}

# Spring Boot 5-field contract
_CONTRACT = ["algorithm_detected", "time_complexity", "issues", "loop_count", "pattern"]


def print_result(result: dict) -> None:
    lang  = result.get("language", "unknown")
    badge = LANG_BADGE.get(lang, f"[{lang.upper()}]")

    print(SEP)

    # Hard error (empty input, size exceeded etc.)
    if "error" in result and "algorithm_detected" not in result:
        print(f"\n  {badge}  {RED}{BOLD}ERROR:{RESET} {result['error']}\n")
        print(SEP)
        return

    # ── Display section ───────────────────────────────────────
    print(f"\n  {badge}")
    print(f"\n{BOLD}  Algorithm  :{RESET} {GREEN}{result.get('algorithm_detected', 'Unknown')}{RESET}")
    print(f"{BOLD}  Complexity :{RESET} {YELLOW}{result.get('time_complexity', 'Unknown')}{RESET}")
    print(f"{BOLD}  Pattern    :{RESET} {result.get('pattern', '')}")

    # loop_depth and is_recursive are in the full schema returned by analyze_code()
    loop_count = result.get("loop_count", 0)
    loop_depth = result.get("loop_depth", 0)
    is_recursive = result.get("is_recursive", False)
    elapsed_ms   = result.get("elapsed_ms", 0.0)

    print(f"{BOLD}  Loop Count :{RESET} {loop_count}  (depth: {loop_depth})")
    print(f"{BOLD}  Recursive  :{RESET} {is_recursive}")

    if result.get("issues"):
        print(f"\n{RED}{BOLD}  Issues:{RESET}")
        for issue in result["issues"]:
            print(f"    {RED}>{RESET} {issue}")

    print(f"\n{DIM}  Analyzed in {elapsed_ms:.2f} ms{RESET}")

    # ── JSON section (exact 5-field Spring Boot contract) ─────
    print(f"\n{DIM}  JSON (Spring Boot contract):{RESET}")
    contract_out = {k: result[k] for k in _CONTRACT if k in result}
    print(json.dumps(contract_out, indent=2, ensure_ascii=False))
    print(SEP)


def interactive() -> None:
    print(f"\n{CYAN}{BOLD}")
    print("  +----------------------------------------------------+")
    print("  |   MULTI-LANGUAGE STATIC ANALYZER  CLI  v2.0       |")
    print("  |   Python · Java · JavaScript · C++                 |")
    print("  +----------------------------------------------------+")
    print(f"{RESET}")

    lang_hint = f"{DIM}python / java / js / cpp  (Enter = auto-detect){RESET}"

    while True:
        print(f"\n  Language [{lang_hint}]: ", end="", flush=True)
        try:
            lang_input = input().strip().lower() or None
        except EOFError:
            sys.exit(0)

        if lang_input == "exit":
            print(f"\n{DIM}  Goodbye!{RESET}\n")
            sys.exit(0)

        print(f"\n  Paste your code below.")
        print(f"  {DIM}Type 'done' on a new line to analyze · 'exit' to quit.{RESET}\n")

        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                sys.exit(0)
            if line.strip().lower() == "exit":
                print(f"\n{DIM}  Goodbye!{RESET}\n")
                sys.exit(0)
            if line.strip().lower() == "done":
                break
            lines.append(line)

        code = "\n".join(lines).strip()
        if not code:
            print(f"\n{YELLOW}  No code entered — try again.{RESET}")
            continue

        print_result(analyze_code(code, language=lang_input))

        print(f"\n  {DIM}Press Enter to analyze another snippet · type 'exit' to quit:{RESET}")
        try:
            again = input().strip().lower()
        except EOFError:
            break
        if again == "exit":
            print(f"\n{DIM}  Goodbye!{RESET}\n")
            break


def main() -> None:
    args      = sys.argv[1:]
    lang      = next((FLAG_MAP[a] for a in args if a in FLAG_MAP), None)
    filepaths = [a for a in args if not a.startswith("--")]

    # File mode
    if filepaths:
        path = filepaths[0]
        if not os.path.isfile(path):
            print(f"\n{RED}  File not found: {path}{RESET}\n")
            sys.exit(1)
        with open(path, encoding="utf-8") as f:
            code = f.read()
        print(f"\n{DIM}  Analyzing: {path}{RESET}")
        print_result(analyze_code(code, language=lang))
        return

    # Pipe mode
    if not sys.stdin.isatty():
        print_result(analyze_code(sys.stdin.read(), language=lang))
        return

    # Interactive
    interactive()


if __name__ == "__main__":
    main()