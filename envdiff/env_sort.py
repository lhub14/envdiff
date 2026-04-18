"""Sort keys in a .env file alphabetically or by group."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class SortResult:
    original_order: List[str]
    sorted_order: List[str]
    changed: bool
    output_lines: List[str]


def _quote_if_needed(value: str) -> str:
    if " " in value or "#" in value or value == "":
        return f'"{value}"'
    return value


def sort_env_file(
    path: Path,
    *,
    group_prefix: bool = False,
    reverse: bool = False,
) -> SortResult:
    """Read *path*, sort its keys, return a SortResult.

    Blank lines and comments are dropped; only key=value lines survive.
    """
    env = parse_env_file(path)
    original_order = list(env.keys())
    sorted_keys = sorted(original_order, reverse=reverse)

    if group_prefix:
        from itertools import groupby

        def _prefix(k: str) -> str:
            return k.split("_")[0]

        sorted_keys = []
        for _pfx, members in groupby(
            sorted(original_order, key=_prefix), key=_prefix
        ):
            sorted_keys.extend(sorted(members, reverse=reverse))

    output_lines: List[str] = []
    for key in sorted_keys:
        output_lines.append(f"{key}={_quote_if_needed(env[key])}")

    return SortResult(
        original_order=original_order,
        sorted_order=sorted_keys,
        changed=original_order != sorted_keys,
        output_lines=output_lines,
    )


def write_sorted(result: SortResult, dest: Path) -> None:
    """Write sorted lines to *dest*."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(result.output_lines) + "\n", encoding="utf-8")
