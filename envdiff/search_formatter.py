"""Format SearchResult for terminal output."""
from __future__ import annotations

from envdiff.env_search import SearchResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_search_result(result: SearchResult, *, colour: bool = True) -> str:
    if not result.matches:
        msg = f"No matches for pattern {result.pattern!r}"
        return _dim(msg) if colour else msg

    lines: list[str] = []
    current_file: str | None = None

    for match in result.matches:
        if match.file != current_file:
            current_file = match.file
            header = f"\n[{current_file}]"
            lines.append(_bold(header) if colour else header)

        tag = f"({match.match_type})"
        key_part = _cyan(match.key) if colour else match.key
        val_part = match.value
        tag_part = _yellow(tag) if colour else tag
        lines.append(f"  {key_part}={val_part}  {tag_part}")

    total = f"\n{len(result.matches)} match(es) for {result.pattern!r}"
    lines.append(_bold(total) if colour else total)
    return "\n".join(lines).lstrip("\n")
