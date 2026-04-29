"""Rank .env files by their diff score relative to a base file."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import compare_envs
from envdiff.score import compute_score


@dataclass
class LeaderboardEntry:
    name: str
    score: int
    grade: str
    missing_in_target: List[str] = field(default_factory=list)
    missing_in_base: List[str] = field(default_factory=list)
    mismatched: List[str] = field(default_factory=list)

    @property
    def total_issues(self) -> int:
        return (
            len(self.missing_in_target)
            + len(self.missing_in_base)
            + len(self.mismatched)
        )


@dataclass
class LeaderboardResult:
    base_name: str
    entries: List[LeaderboardEntry] = field(default_factory=list)

    @property
    def winner(self) -> LeaderboardEntry | None:
        return self.entries[0] if self.entries else None


def build_leaderboard(
    base: Dict[str, str],
    targets: Dict[str, Dict[str, str]],
    base_name: str = "base",
    compare_values: bool = True,
) -> LeaderboardResult:
    """Rank each target env against the base by score (descending)."""
    entries: List[LeaderboardEntry] = []

    for name, env in targets.items():
        diff = compare_envs(base, env, compare_values=compare_values)
        score_result = compute_score(diff)
        entry = LeaderboardEntry(
            name=name,
            score=score_result.score,
            grade=score_result.grade,
            missing_in_target=list(diff.missing_in_target),
            missing_in_base=list(diff.missing_in_base),
            mismatched=list(diff.mismatched.keys()),
        )
        entries.append(entry)

    entries.sort(key=lambda e: (-e.score, e.name))
    return LeaderboardResult(base_name=base_name, entries=entries)
