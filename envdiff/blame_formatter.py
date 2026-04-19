"""Format a BlameResult for terminal output."""
from __future__ import annotations

from envdiff.env_diff_blame import BlameResult


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


_KIND_LABEL = {
    "missing_in_target": "missing in target",
    "missing_in_base": "missing in base",
    "mismatch": "value mismatch",
}


def format_blame_result(result: BlameResult, *, colour: bool = True) -> str:
    if not result.entries:
        return "No differences to blame.\n"

    lines: list[str] = []
    for entry in result.entries:
        label = _KIND_LABEL.get(entry.kind, entry.kind)
        key_str = _yellow(entry.key) if colour else entry.key
        kind_str = _red(f"[{label}]") if colour else f"[{label}]"

        author_info = ""
        if entry.author or entry.commit:
            parts = []
            if entry.commit:
                parts.append(entry.commit)
            if entry.author:
                parts.append(entry.author)
            raw = "  " + " ".join(parts)
            author_info = _dim(raw) if colour else raw

        lines.append(f"{key_str} {kind_str}{author_info}")

    return "\n".join(lines) + "\n"
