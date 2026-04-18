"""Format NormalizeResult for terminal output."""
from __future__ import annotations

from envdiff.env_normalize import NormalizeResult, has_changes


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_normalize_result(result: NormalizeResult, *, colour: bool = True) -> str:
    lines: list[str] = []

    if not has_changes(result) and not result.duplicates_removed:
        msg = "✓ File is already normalized."
        return _green(msg) if colour else msg

    if result.changes:
        lines.append(("Changes:" if not colour else _yellow("Changes:")))
        for key, reason in result.changes:
            lines.append(f"  {key}: {_dim(reason) if colour else reason}")

    if result.duplicates_removed:
        label = "Duplicates removed:" if not colour else _yellow("Duplicates removed:")
        lines.append(label)
        for key in result.duplicates_removed:
            lines.append(f"  {key}")

    return "\n".join(lines)
