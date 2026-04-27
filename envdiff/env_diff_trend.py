"""Compute trend data across a sequence of diff snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from envdiff.comparator import DiffResult


@dataclass
class TrendPoint:
    label: str
    missing_in_target: int
    missing_in_base: int
    mismatched: int

    @property
    def total_issues(self) -> int:
        return self.missing_in_target + self.missing_in_base + self.mismatched


@dataclass
class TrendResult:
    points: List[TrendPoint] = field(default_factory=list)


def has_trend_data(result: TrendResult) -> bool:
    return len(result.points) > 0


def is_improving(result: TrendResult) -> bool:
    """Return True if the most recent point has fewer issues than the first."""
    if len(result.points) < 2:
        return False
    return result.points[-1].total_issues < result.points[0].total_issues


def is_degrading(result: TrendResult) -> bool:
    """Return True if the most recent point has more issues than the first."""
    if len(result.points) < 2:
        return False
    return result.points[-1].total_issues > result.points[0].total_issues


def build_trend(labeled_diffs: List[tuple[str, DiffResult]]) -> TrendResult:
    """Build a TrendResult from a sequence of (label, DiffResult) pairs."""
    points: List[TrendPoint] = []
    for label, diff in labeled_diffs:
        points.append(
            TrendPoint(
                label=label,
                missing_in_target=len(diff.missing_in_target),
                missing_in_base=len(diff.missing_in_base),
                mismatched=len(diff.mismatched),
            )
        )
    return TrendResult(points=points)
