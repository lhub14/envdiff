"""Compute key coverage metrics across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class CoverageRow:
    key: str
    present_in: List[str]
    missing_from: List[str]

    @property
    def coverage_ratio(self) -> float:
        total = len(self.present_in) + len(self.missing_from)
        if total == 0:
            return 1.0
        return len(self.present_in) / total

    @property
    def is_full(self) -> bool:
        return len(self.missing_from) == 0


@dataclass
class CoverageResult:
    rows: List[CoverageRow] = field(default_factory=list)
    file_names: List[str] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return len(self.rows)

    @property
    def fully_covered(self) -> int:
        return sum(1 for r in self.rows if r.is_full)

    @property
    def overall_ratio(self) -> float:
        if not self.rows:
            return 1.0
        return self.fully_covered / self.total_keys


def compute_coverage(
    envs: Dict[str, Dict[str, str]],
) -> CoverageResult:
    """Compute per-key coverage across *envs* (mapping of label -> parsed env)."""
    if not envs:
        return CoverageResult()

    file_names = list(envs.keys())
    all_keys: Set[str] = set()
    for parsed in envs.values():
        all_keys.update(parsed.keys())

    rows: List[CoverageRow] = []
    for key in sorted(all_keys):
        present_in = [name for name, parsed in envs.items() if key in parsed]
        missing_from = [name for name in file_names if name not in present_in]
        rows.append(CoverageRow(key=key, present_in=present_in, missing_from=missing_from))

    return CoverageResult(rows=rows, file_names=file_names)
