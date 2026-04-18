"""Format SuggestResult for terminal output."""
from __future__ import annotations

from envdiff.suggest import SuggestResult


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_suggest_result(result: SuggestResult, *, colour: bool = True) -> str:
    lines: list[str] = []

    if not result.suggestions and not result.unmatched:
        msg = "No missing keys to suggest defaults for."
        return _green(msg) if colour else msg

    if result.suggestions:
        lines.append("Suggested defaults:")
        for s in result.suggestions:
            key_part = _green(s.key) if colour else s.key
            val_part = s.value
            hint = _dim(f"  # {s.reason}") if colour else f"  # {s.reason}"
            lines.append(f"  {key_part}={val_part}{hint}")

    if result.unmatched:
        lines.append("No suggestion available:")
        for key in result.unmatched:
            k = _yellow(key) if colour else key
            lines.append(f"  {k}")

    return "\n".join(lines)
