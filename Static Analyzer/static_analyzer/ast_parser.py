"""
ast_parser.py
-------------
Parses raw Python source code into an Abstract Syntax Tree (AST).
Provides structured error context on failure.
"""

import ast
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ParseError:
    """Structured representation of a parse failure."""
    message: str
    line: Optional[int] = None
    offset: Optional[int] = None
    text: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "line": self.line,
            "offset": self.offset,
            "text": self.text,
        }


def parse_code(code: str) -> tuple[Optional[ast.AST], Optional[ParseError]]:
    """
    Parse Python source code into an AST.

    Args:
        code: Raw Python source code string.

    Returns:
        A tuple of (ast.AST, None) on success,
        or (None, ParseError) on failure.
    """
    if not isinstance(code, str):
        logger.warning("parse_code received non-string input: %s", type(code))
        return None, ParseError(message="Input must be a string.")

    stripped = code.strip()
    if not stripped:
        logger.debug("Empty code submitted for parsing.")
        return None, ParseError(message="Code input is empty.")

    try:
        tree = ast.parse(stripped)
        logger.debug("Successfully parsed code (%d chars).", len(stripped))
        return tree, None

    except SyntaxError as exc:
        logger.info("Syntax error while parsing code: %s", exc)
        return None, ParseError(
            message=f"SyntaxError: {exc.msg}",
            line=exc.lineno,
            offset=exc.offset,
            text=exc.text,
        )

    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error during AST parsing.")
        return None, ParseError(message=f"Unexpected parse error: {exc}")
