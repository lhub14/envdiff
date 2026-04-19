"""Format TransformResult for terminal output."""
from __future__ import annotations

from envdiff.env_transform import TransformResult


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_transform_result(result: TransformResult, *, colour: bool = True) -> str:
    lines: list[str] = []
    if not result.changes:
        msg = "No changes applied."
        return _dim(msg) if colour else msg

    lines.append(("Changes applied:" if not colour else _green("Changes applied:")))
    for change in result.changes:
        prefix = "  ~ "
        lines.append((_yellow(prefix) if colour else prefix) + change)
    return "\n".join(lines)
