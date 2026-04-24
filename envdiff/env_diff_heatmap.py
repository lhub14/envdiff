"""Heatmap: score each key by how often it differs across many env comparisons."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

from envdiff.comparator import DiffResult


@dataclass
class HeatmapRow:
    key: str
    diff_count: int
    total: int

    @property
    def ratio(self) -> float:
        return self.diff_count / self.total if self.total else 0.0

    @property
    def heat(self) -> str:
        r = self.ratio
        if r == 0.0:
            return "cold"
        if r < 0.4:
            return "warm"
        if r < 0.8:
            return "hot"
        return "critical"


@dataclass
class HeatmapResult:
    rows: List[HeatmapRow] = field(default_factory=list)
    total_comparisons: int = 0


def build_heatmap(diffs: Sequence[DiffResult]) -> HeatmapResult:
    """Aggregate multiple DiffResults into a per-key heat score."""
    total = len(diffs)
    counts: Dict[str, int] = {}

    for diff in diffs:
        touched: set[str] = set()
        touched.update(diff.missing_in_target)
        touched.update(diff.missing_in_base)
        touched.update(diff.mismatched.keys())
        for key in touched:
            counts[key] = counts.get(key, 0) + 1

    rows = [
        HeatmapRow(key=k, diff_count=v, total=total)
        for k, v in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    ]
    return HeatmapResult(rows=rows, total_comparisons=total)


def has_hot_keys(result: HeatmapResult) -> bool:
    return any(r.heat in ("hot", "critical") for r in result.rows)
