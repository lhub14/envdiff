"""Compute key overlap statistics between multiple .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class OverlapRow:
    key: str
    files: List[str]          # files that contain this key
    total_files: int

    @property
    def overlap_ratio(self) -> float:
        if self.total_files == 0:
            return 0.0
        return len(self.files) / self.total_files

    @property
    def is_universal(self) -> bool:
        return len(self.files) == self.total_files

    @property
    def is_unique(self) -> bool:
        return len(self.files) == 1


@dataclass
class OverlapResult:
    rows: List[OverlapRow] = field(default_factory=list)
    file_names: List[str] = field(default_factory=list)

    @property
    def universal_keys(self) -> List[str]:
        return [r.key for r in self.rows if r.is_universal]

    @property
    def unique_keys(self) -> List[str]:
        return [r.key for r in self.rows if r.is_unique]

    @property
    def partial_keys(self) -> List[str]:
        return [r.key for r in self.rows if not r.is_universal and not r.is_unique]


def compute_overlap(envs: Dict[str, Dict[str, str]]) -> OverlapResult:
    """Given a mapping of filename -> parsed env dict, compute key overlap."""
    if not envs:
        return OverlapResult()

    file_names = list(envs.keys())
    total = len(file_names)
    key_to_files: Dict[str, List[str]] = {}

    for fname, env in envs.items():
        for key in env:
            key_to_files.setdefault(key, []).append(fname)

    rows = [
        OverlapRow(key=k, files=sorted(v), total_files=total)
        for k, v in sorted(key_to_files.items())
    ]
    return OverlapResult(rows=rows, file_names=file_names)
