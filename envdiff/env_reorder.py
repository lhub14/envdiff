"""Reorder .env file keys to match a reference file's key order."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class ReorderResult:
    original_lines: List[str]
    reordered_lines: List[str]
    moved_keys: List[str]
    appended_keys: List[str]  # keys not in reference, appended at end
    changed: bool


def _quote_if_needed(value: str) -> str:
    if " " in value or "#" in value or value == "":
        return f'"{value}"'
    return value


def reorder_env(
    source: Dict[str, str],
    reference_order: List[str],
    comments: Optional[Dict[str, str]] = None,
) -> ReorderResult:
    """Return a ReorderResult aligning source keys to reference_order."""
    comments = comments or {}
    original_keys = list(source.keys())
    original_lines = [
        f"{k}={_quote_if_needed(v)}" for k, v in source.items()
    ]

    ordered: List[str] = []
    moved: List[str] = []

    for key in reference_order:
        if key in source:
            ordered.append(key)
            if original_keys.index(key) != len(moved):
                moved.append(key)

    appended: List[str] = [
        k for k in original_keys if k not in reference_order
    ]

    final_keys = ordered + appended
    reordered_lines = [
        f"{k}={_quote_if_needed(source[k])}" for k in final_keys
    ]

    return ReorderResult(
        original_lines=original_lines,
        reordered_lines=reordered_lines,
        moved_keys=moved,
        appended_keys=appended,
        changed=reordered_lines != original_lines,
    )


def reorder_env_file(
    source_path: Path,
    reference_path: Path,
) -> ReorderResult:
    source = parse_env_file(source_path)
    reference = parse_env_file(reference_path)
    reference_order = list(reference.keys())
    return reorder_env(source, reference_order)


def write_reordered(result: ReorderResult, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(result.reordered_lines) + "\n", encoding="utf-8")
