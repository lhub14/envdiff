"""Detect keys that appear to be aliases of each other across env files.

An alias is a key whose value matches another key's value in the same or
different env file, suggesting one may be a duplicate or legacy name.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class AliasGroup:
    """A group of keys that share the same value."""
    value: str
    keys: List[Tuple[str, str]]  # (filename, key)


@dataclass
class AliasResult:
    groups: List[AliasGroup] = field(default_factory=list)
    checked: int = 0


def has_aliases(result: AliasResult) -> bool:
    return len(result.groups) > 0


def detect_aliases(
    envs: Dict[str, Dict[str, str]],
    min_length: int = 3,
) -> AliasResult:
    """Find keys sharing identical non-trivial values across all provided envs.

    Args:
        envs: mapping of filename -> parsed env dict.
        min_length: minimum value length to consider (avoids flagging empty /
                    single-char values like "1" or "true").
    """
    # Build an inverted index: value -> [(filename, key), ...]
    index: Dict[str, List[Tuple[str, str]]] = {}
    total = 0

    for filename, env in envs.items():
        for key, value in env.items():
            total += 1
            if len(value) < min_length:
                continue
            index.setdefault(value, []).append((filename, key))

    groups: List[AliasGroup] = [
        AliasGroup(value=val, keys=entries)
        for val, entries in index.items()
        if len(entries) > 1
    ]
    # Sort for deterministic output
    groups.sort(key=lambda g: g.value)

    return AliasResult(groups=groups, checked=total)
