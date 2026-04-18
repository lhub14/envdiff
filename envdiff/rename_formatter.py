"""Format RenameResult for terminal output."""
from __future__ import annotations

from envdiff.rename import RenameResult


def _yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"


def _dim(text: str) -> str:
    return f"\033[2m{text}\033[0m"


def format_rename_result(result: RenameResult) -> str:
    lines: list[str] = []

    if not result.candidates:
        lines.append("No rename candidates found.")
    else:
        lines.append("Rename candidates:")
        for c in result.candidates:
            bar = int(c.score * 10)
            meter = "[" + "#" * bar + "-" * (10 - bar) + "]"
            lines.append(
                f"  {_yellow(c.old_key)} -> {_yellow(c.new_key)}  "
                f"{_dim(meter)} {c.score:.0%}"
            )

    if result.unmatched_base:
        lines.append("")
        lines.append("Unmatched (only in base):")
        for k in result.unmatched_base:
            lines.append(f"  - {k}")

    if result.unmatched_target:
        lines.append("")
        lines.append("Unmatched (only in target):")
        for k in result.unmatched_target:
            lines.append(f"  + {k}")

    return "\n".join(lines)
