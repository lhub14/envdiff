"""Format StatsResult for terminal output."""
from __future__ import annotations

from envdiff.stats import StatsResult


def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


def _cyan(text: str) -> str:
    return f"\033[36m{text}\033[0m"


def _yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"


def format_stats(result: StatsResult, *, colour: bool = True) -> str:
    lines: list[str] = []

    def c(fn, text):
        return fn(text) if colour else text

    lines.append(c(_bold, f"Total unique keys across all files: {len(result.all_keys)}"))
    lines.append(c(_bold, f"Keys present in ALL files: {len(result.common_keys)}"))
    if result.common_keys:
        lines.append("  " + ", ".join(result.common_keys))
    lines.append("")

    for fs in result.files:
        lines.append(c(_cyan, f"File: {fs.file}"))
        lines.append(f"  Total keys   : {fs.total_keys}")
        lines.append(f"  Empty values : {fs.empty_values}")
        lines.append(f"  Sensitive    : {fs.sensitive_keys}")
        if fs.unique_keys:
            lines.append(c(_yellow, f"  Unique keys  : {', '.join(fs.unique_keys)}"))
        lines.append("")

    return "\n".join(lines).rstrip()
