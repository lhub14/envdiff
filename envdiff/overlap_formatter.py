"""Text formatter for OverlapResult."""
from __future__ import annotations

from envdiff.env_diff_overlap import OverlapResult


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def format_overlap_result(result: OverlapResult, *, colour: bool = True) -> str:
    if not result.rows:
        return "No keys found."

    lines: list[str] = []
    n = len(result.file_names)
    lines.append(_bold(f"Key overlap across {n} file(s):") if colour else f"Key overlap across {n} file(s):")
    lines.append("")

    for row in result.rows:
        pct = f"{row.overlap_ratio * 100:.0f}%"
        present = f"{len(row.files)}/{row.total_files}"
        tag = f"[{present:>5}  {pct:>4}]"

        if colour:
            if row.is_universal:
                tag = _green(tag)
            elif row.is_unique:
                tag = _red(tag)
            else:
                tag = _yellow(tag)

        lines.append(f"  {tag}  {row.key}")

    lines.append("")
    lines.append(f"Universal : {len(result.universal_keys)}")
    lines.append(f"Partial   : {len(result.partial_keys)}")
    lines.append(f"Unique    : {len(result.unique_keys)}")
    return "\n".join(lines)
