"""Build a tabular summary comparing multiple .env files side-by-side."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SummaryTableRow:
    key: str
    values: Dict[str, Optional[str]]  # filename -> value or None if missing

    @property
    def is_uniform(self) -> bool:
        present = [v for v in self.values.values() if v is not None]
        return len(present) > 0 and len(set(present)) == 1

    @property
    def is_complete(self) -> bool:
        return all(v is not None for v in self.values.values())

    @property
    def missing_in(self) -> List[str]:
        return [fname for fname, v in self.values.items() if v is None]


@dataclass
class SummaryTableResult:
    filenames: List[str]
    rows: List[SummaryTableRow] = field(default_factory=list)

    @property
    def total_keys(self) -> int:
        return len(self.rows)

    @property
    def uniform_keys(self) -> int:
        return sum(1 for r in self.rows if r.is_uniform and r.is_complete)

    @property
    def incomplete_keys(self) -> int:
        return sum(1 for r in self.rows if not r.is_complete)

    @property
    def mismatched_keys(self) -> int:
        return sum(1 for r in self.rows if r.is_complete and not r.is_uniform)


def build_summary_table(
    envs: Dict[str, Dict[str, str]],
) -> SummaryTableResult:
    """Build a SummaryTableResult from a mapping of filename -> parsed env dict."""
    filenames = list(envs.keys())
    all_keys: List[str] = sorted(
        {k for env in envs.values() for k in env}
    )
    rows: List[SummaryTableRow] = []
    for key in all_keys:
        values = {fname: envs[fname].get(key) for fname in filenames}
        rows.append(SummaryTableRow(key=key, values=values))
    return SummaryTableResult(filenames=filenames, rows=rows)
