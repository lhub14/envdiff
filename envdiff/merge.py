"""Merge multiple .env files into one, with conflict detection."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class MergeResult:
    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: Dict[str, List[Tuple[str, str]]] = field(default_factory=dict)  # key -> [(source, value)]


def has_conflicts(result: MergeResult) -> bool:
    return bool(result.conflicts)


def merge_envs(sources: Dict[str, Dict[str, str]], strategy: str = "first") -> MergeResult:
    """Merge named env dicts.

    strategy:
      'first'  – keep the first value seen (default)
      'last'   – keep the last value seen
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}")

    merged: Dict[str, str] = {}
    conflicts: Dict[str, List[Tuple[str, str]]] = {}
    seen: Dict[str, str] = {}  # key -> source name

    for source_name, env in sources.items():
        for key, value in env.items():
            if key not in merged:
                merged[key] = value
                seen[key] = source_name
            else:
                existing_value = merged[key]
                if existing_value != value:
                    if key not in conflicts:
                        conflicts[key] = [(seen[key], existing_value)]
                    conflicts[key].append((source_name, value))
                    if strategy == "last":
                        merged[key] = value
                        seen[key] = source_name

    return MergeResult(merged=merged, conflicts=conflicts)
