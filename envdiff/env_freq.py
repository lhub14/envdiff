"""Frequency analysis: how often each key appears across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple

from envdiff.parser import parse_env_file


@dataclass
class FreqRow:
    key: str
    count: int
    total: int
    files: List[str] = field(default_factory=list)

    @property
    def ratio(self) -> float:
        return self.count / self.total if self.total else 0.0

    @property
    def is_universal(self) -> bool:
        return self.count == self.total

    @property
    def is_unique(self) -> bool:
        return self.count == 1


@dataclass
class FreqResult:
    rows: List[FreqRow] = field(default_factory=list)
    total_files: int = 0

    @property
    def universal_keys(self) -> List[str]:
        return [r.key for r in self.rows if r.is_universal]

    @property
    def unique_keys(self) -> List[str]:
        return [r.key for r in self.rows if r.is_unique]


def compute_freq(env_files: Sequence[Tuple[str, str]]) -> FreqResult:
    """Compute key frequency across env files.

    Args:
        env_files: sequence of (label, path) pairs.

    Returns:
        FreqResult with rows sorted by descending count then key name.
    """
    total = len(env_files)
    key_info: Dict[str, List[str]] = {}

    for label, path in env_files:
        try:
            env = parse_env_file(path)
        except Exception:
            continue
        for key in env:
            key_info.setdefault(key, []).append(label)

    rows = [
        FreqRow(
            key=k,
            count=len(labels),
            total=total,
            files=sorted(labels),
        )
        for k, labels in key_info.items()
    ]
    rows.sort(key=lambda r: (-r.count, r.key))
    return FreqResult(rows=rows, total_files=total)
