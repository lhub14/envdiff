"""Detect drift: keys present in baseline but removed from current env."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from envdiff.baseline import Baseline


@dataclass
class DriftResult:
    label: str
    added: List[str] = field(default_factory=list)    # in current, not in baseline
    removed: List[str] = field(default_factory=list)  # in baseline, not in current
    changed: List[str] = field(default_factory=list)  # value differs

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def detect_drift(
    current: Dict[str, str],
    baseline: Baseline,
    label: str,
    *,
    check_values: bool = True,
) -> DriftResult:
    """Compare *current* env dict against a saved *baseline* snapshot."""
    if label not in baseline.snapshots:
        raise KeyError(f"Label {label!r} not found in baseline store.")

    snap: Dict[str, str] = baseline.snapshots[label]
    current_keys: Set[str] = set(current)
    snap_keys: Set[str] = set(snap)

    result = DriftResult(label=label)
    result.added = sorted(current_keys - snap_keys)
    result.removed = sorted(snap_keys - current_keys)

    if check_values:
        for key in sorted(current_keys & snap_keys):
            if current[key] != snap[key]:
                result.changed.append(key)

    return result
