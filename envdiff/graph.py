"""Dependency graph: detect which keys are shared across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set


@dataclass
class GraphResult:
    # key -> set of file labels that define it
    key_presence: Dict[str, Set[str]] = field(default_factory=dict)
    # keys present in ALL files
    universal: FrozenSet[str] = frozenset()
    # keys present in exactly ONE file
    unique: Dict[str, str] = field(default_factory=dict)  # key -> label
    # keys present in SOME but not all files
    partial: Dict[str, Set[str]] = field(default_factory=dict)


def build_graph(envs: Dict[str, Dict[str, str]]) -> GraphResult:
    """Build a presence graph from a mapping of label -> parsed env dict."""
    if not envs:
        return GraphResult()

    labels = list(envs.keys())
    key_presence: Dict[str, Set[str]] = {}

    for label, env in envs.items():
        for key in env:
            key_presence.setdefault(key, set()).add(label)

    all_labels = set(labels)
    universal: Set[str] = set()
    unique: Dict[str, str] = {}
    partial: Dict[str, Set[str]] = {}

    for key, present_in in key_presence.items():
        if present_in == all_labels:
            universal.add(key)
        elif len(present_in) == 1:
            unique[key] = next(iter(present_in))
        else:
            partial[key] = present_in

    return GraphResult(
        key_presence=key_presence,
        universal=frozenset(universal),
        unique=unique,
        partial=partial,
    )


def shared_ratio(result: GraphResult, total_files: int) -> float:
    """Fraction of keys that are universal across all files."""
    total = len(result.key_presence)
    if total == 0:
        return 1.0
    return len(result.universal) / total
