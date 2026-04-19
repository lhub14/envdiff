"""Detect and remove duplicate values across keys in an env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DedupResult:
    """Result of a deduplication scan."""
    duplicates: Dict[str, List[str]] = field(default_factory=dict)
    # value -> list of keys that share it

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)


def find_duplicate_values(env: Dict[str, str]) -> DedupResult:
    """Find keys that share identical non-empty values."""
    value_map: Dict[str, List[str]] = {}
    for key, value in env.items():
        if value == "":
            continue
        value_map.setdefault(value, []).append(key)

    duplicates = {v: keys for v, keys in value_map.items() if len(keys) > 1}
    return DedupResult(duplicates=duplicates)


def deduplicate_env(
    env: Dict[str, str],
    keep: str = "first",
) -> Tuple[Dict[str, str], List[str]]:
    """Return a new env dict with duplicate-value keys removed.

    Args:
        env: Parsed env mapping.
        keep: ``'first'`` keeps the first key encountered for each value;
              ``'last'`` keeps the last.

    Returns:
        Tuple of (cleaned env dict, list of removed keys).
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    result = find_duplicate_values(env)
    removed: List[str] = []

    keys_to_remove: set[str] = set()
    for keys in result.duplicates.values():
        ordered = keys if keep == "first" else list(reversed(keys))
        # drop all but the first in ordered
        for k in ordered[1:]:
            keys_to_remove.add(k)

    cleaned = {k: v for k, v in env.items() if k not in keys_to_remove}
    removed = [k for k in env if k in keys_to_remove]
    return cleaned, removed
