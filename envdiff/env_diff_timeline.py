"""Build a timeline of diff results across multiple snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from envdiff.comparator import DiffResult, compare_envs
from envdiff.snapshot import load_snapshots


@dataclass
class TimelineEntry:
    label: str
    timestamp: str
    missing_in_target: List[str]
    missing_in_base: List[str]
    mismatched: List[str]

    @property
    def total_issues(self) -> int:
        return len(self.missing_in_target) + len(self.missing_in_base) + len(self.mismatched)

    @property
    def is_clean(self) -> bool:
        return self.total_issues == 0


@dataclass
class TimelineResult:
    base_label: str
    entries: List[TimelineEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(not e.is_clean for e in self.entries)

    @property
    def worst_entry(self) -> Optional[TimelineEntry]:
        if not self.entries:
            return None
        return max(self.entries, key=lambda e: e.total_issues)


def build_timeline(
    store_path: str,
    base_label: str,
    target_labels: Optional[List[str]] = None,
    ignore_values: bool = False,
) -> TimelineResult:
    """Compare a base snapshot against one or more target snapshots."""
    snapshots = load_snapshots(store_path)

    if base_label not in snapshots:
        raise KeyError(f"Base label '{base_label}' not found in snapshot store.")

    base_env = snapshots[base_label]["env"]

    labels = target_labels if target_labels else [
        lbl for lbl in snapshots if lbl != base_label
    ]

    result = TimelineResult(base_label=base_label)

    for label in labels:
        if label not in snapshots:
            continue
        entry_data = snapshots[label]
        target_env = entry_data["env"]
        diff: DiffResult = compare_envs(
            base_env, target_env, compare_values=not ignore_values
        )
        result.entries.append(
            TimelineEntry(
                label=label,
                timestamp=entry_data.get("timestamp", ""),
                missing_in_target=list(diff.missing_in_target),
                missing_in_base=list(diff.missing_in_base),
                mismatched=list(diff.mismatched),
            )
        )

    result.entries.sort(key=lambda e: e.timestamp)
    return result
