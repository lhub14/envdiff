"""Normalize .env files: trim whitespace, sort, deduplicate, and standardize quoting."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from envdiff.parser import parse_env_file


@dataclass
class NormalizeResult:
    original_lines: List[str]
    normalized_lines: List[str]
    changes: List[Tuple[str, str]]  # (key, reason)
    duplicates_removed: List[str]


def has_changes(result: NormalizeResult) -> bool:
    return result.normalized_lines != result.original_lines


def _needs_quoting(value: str) -> bool:
    return " " in value or "#" in value or value == ""


def _normalize_line(line: str) -> Tuple[str, str | None]:
    """Return (normalized_line, reason) where reason is None if unchanged."""
    stripped = line.rstrip()
    if not stripped or stripped.lstrip().startswith("#"):
        return stripped, None
    if "=" not in stripped:
        return stripped, None
    key, _, value = stripped.partition("=")
    key_clean = key.strip()
    value_clean = value.strip()
    # Strip surrounding quotes for normalization
    if len(value_clean) >= 2 and value_clean[0] in ('"', "'") and value_clean[-1] == value_clean[0]:
        value_clean = value_clean[1:-1]
    normalized_value = f'"{value_clean}"' if _needs_quoting(value_clean) else value_clean
    normalized = f"{key_clean}={normalized_value}"
    reason = None if normalized == stripped else "normalized whitespace/quoting"
    return normalized, reason


def normalize_env(path: Path) -> NormalizeResult:
    raw = path.read_text(encoding="utf-8")
    original_lines = raw.splitlines()
    seen_keys: Dict[str, int] = {}
    normalized_lines: List[str] = []
    changes: List[Tuple[str, str]] = []
    duplicates_removed: List[str] = []

    for line in original_lines:
        norm, reason = _normalize_line(line)
        if "=" in norm and not norm.lstrip().startswith("#"):
            key = norm.partition("=")[0].strip()
            if key in seen_keys:
                duplicates_removed.append(key)
                continue
            seen_keys[key] = 1
        if reason:
            key = norm.partition("=")[0].strip()
            changes.append((key, reason))
        normalized_lines.append(norm)

    return NormalizeResult(
        original_lines=original_lines,
        normalized_lines=normalized_lines,
        changes=changes,
        duplicates_removed=duplicates_removed,
    )


def write_normalized(result: NormalizeResult, path: Path) -> None:
    path.write_text("\n".join(result.normalized_lines) + "\n", encoding="utf-8")
