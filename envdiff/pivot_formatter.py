"""Format a PivotResult for terminal output."""
from __future__ import annotations

from typing import List

from envdiff.env_pivot import PivotResult, PivotRow

_MISSING = "(missing)"
_SEP = "  "


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cell(value: str | None, uniform: bool) -> str:
    if value is None:
        return _red(_MISSING)
    if not uniform:
        return _yellow(value)
    return value


def format_pivot(result: PivotResult, *, colour: bool = True) -> str:
    if not result.rows:
        return "No keys found.\n"

    col_width = max(len(f) for f in result.filenames)
    key_width = max(len(r.key) for r in result.rows)

    header_parts = [_bold("KEY").ljust(key_width + 10)] if colour else ["KEY".ljust(key_width)]
    for fname in result.filenames:
        header_parts.append(fname.ljust(col_width))
    lines: List[str] = [_SEP.join(header_parts)]
    lines.append("-" * (key_width + col_width * len(result.filenames) + len(_SEP) * len(result.filenames)))

    for row in result.rows:
        uniform = row.is_uniform
        key_label = _bold(row.key) if colour else row.key
        parts = [key_label.ljust(key_width + (10 if colour else 0))]
        for fname in result.filenames:
            raw = row.values.get(fname)
            cell = _cell(raw, uniform) if colour else (raw if raw is not None else _MISSING)
            parts.append(cell.ljust(col_width))
        lines.append(_SEP.join(parts))

    return "\n".join(lines) + "\n"
