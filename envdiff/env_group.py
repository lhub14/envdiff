"""Group env keys by prefix and report per-group statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GroupResult:
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)


def group_by_prefix(
    env: Dict[str, str],
    prefixes: List[str],
    *,
    strip_prefix: bool = False,
) -> GroupResult:
    """Partition *env* keys into named buckets based on *prefixes*.

    Keys that match no prefix land in ``ungrouped``.
    If *strip_prefix* is True the prefix is removed from the stored key name.
    """
    groups: Dict[str, List[str]] = {p: [] for p in prefixes}
    ungrouped: List[str] = []

    for key in sorted(env):
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix):
                stored = key[len(prefix):] if strip_prefix else key
                groups[prefix].append(stored)
                matched = True
                break
        if not matched:
            ungrouped.append(key)

    return GroupResult(groups=groups, ungrouped=ungrouped)


def format_group_result(result: GroupResult) -> str:
    lines: List[str] = []
    for prefix, keys in result.groups.items():
        lines.append(f"[{prefix}] ({len(keys)} keys)")
        for k in keys:
            lines.append(f"  {k}")
    if result.ungrouped:
        lines.append(f"[ungrouped] ({len(result.ungrouped)} keys)")
        for k in result.ungrouped:
            lines.append(f"  {k}")
    return "\n".join(lines) if lines else "No keys."
