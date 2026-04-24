"""Build a key-by-environment matrix showing presence and value agreement."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MatrixCell:
    present: bool
    value: Optional[str]


@dataclass
class MatrixRow:
    key: str
    cells: Dict[str, MatrixCell] = field(default_factory=dict)

    @property
    def is_uniform(self) -> bool:
        """All present cells share the same value."""
        values = {c.value for c in self.cells.values() if c.present}
        return len(values) <= 1

    @property
    def is_complete(self) -> bool:
        """Key is present in every environment."""
        return all(c.present for c in self.cells.values())

    @property
    def missing_in(self) -> List[str]:
        return [name for name, c in self.cells.items() if not c.present]


@dataclass
class MatrixResult:
    env_names: List[str]
    rows: List[MatrixRow] = field(default_factory=list)

    @property
    def has_gaps(self) -> bool:
        return any(not r.is_complete for r in self.rows)

    @property
    def has_mismatches(self) -> bool:
        return any(not r.is_uniform for r in self.rows)


def build_matrix(envs: Dict[str, Dict[str, str]]) -> MatrixResult:
    """Build a MatrixResult from a mapping of env-name -> parsed env dict."""
    names = list(envs.keys())
    all_keys: List[str] = sorted({k for env in envs.values() for k in env})

    rows: List[MatrixRow] = []
    for key in all_keys:
        row = MatrixRow(key=key)
        for name in names:
            env = envs[name]
            if key in env:
                row.cells[name] = MatrixCell(present=True, value=env[key])
            else:
                row.cells[name] = MatrixCell(present=False, value=None)
        rows.append(row)

    return MatrixResult(env_names=names, rows=rows)
