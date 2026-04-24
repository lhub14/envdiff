"""Pivot .env data: transpose keys vs files into a comparison matrix."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PivotRow:
    key: str
    values: Dict[str, Optional[str]]  # filename -> value or None if missing

    @property
    def is_uniform(self) -> bool:
        """True when all present values are identical."""
        present = [v for v in self.values.values() if v is not None]
        return len(set(present)) <= 1

    @property
    def is_complete(self) -> bool:
        """True when the key exists in every file."""
        return all(v is not None for v in self.values.values())


@dataclass
class PivotResult:
    filenames: List[str]
    rows: List[PivotRow] = field(default_factory=list)

    @property
    def has_gaps(self) -> bool:
        return any(not r.is_complete for r in self.rows)

    @property
    def has_mismatches(self) -> bool:
        return any(not r.is_uniform for r in self.rows)


def pivot_envs(envs: Dict[str, Dict[str, str]]) -> PivotResult:
    """Build a pivot table from a mapping of filename -> parsed env dict."""
    filenames = list(envs.keys())
    all_keys: List[str] = []
    seen: set = set()
    for env in envs.values():
        for k in env:
            if k not in seen:
                all_keys.append(k)
                seen.add(k)

    rows: List[PivotRow] = []
    for key in sorted(all_keys):
        values = {fname: envs[fname].get(key) for fname in filenames}
        rows.append(PivotRow(key=key, values=values))

    return PivotResult(filenames=filenames, rows=rows)
