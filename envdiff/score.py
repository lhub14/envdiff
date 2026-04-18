"""Compute a health score for an env file compared to a base."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from envdiff.comparator import DiffResult


@dataclass
class ScoreResult:
    total_keys: int
    missing_in_target: int
    missing_in_base: int
    mismatched: int
    score: float  # 0.0 – 100.0
    grade: str


_GRADE_THRESHOLDS = [
    (95.0, "A"),
    (80.0, "B"),
    (60.0, "C"),
    (40.0, "D"),
    (0.0, "F"),
]


def _grade(score: float) -> str:
    for threshold, letter in _GRADE_THRESHOLDS:
        if score >= threshold:
            return letter
    return "F"


def compute_score(base: Dict[str, str], diff: DiffResult) -> ScoreResult:
    """Return a ScoreResult reflecting how closely *target* matches *base*."""
    total = len(base)
    if total == 0:
        return ScoreResult(
            total_keys=0,
            missing_in_target=0,
            missing_in_base=len(diff.missing_in_base),
            mismatched=len(diff.mismatched),
            score=100.0,
            grade="A",
        )

    missing_t = len(diff.missing_in_target)
    missing_b = len(diff.missing_in_base)
    mismatched = len(diff.mismatched)

    penalty = missing_t * 2 + mismatched
    raw = max(0.0, (total * 2 - penalty) / (total * 2)) * 100.0
    score = round(raw, 1)

    return ScoreResult(
        total_keys=total,
        missing_in_target=missing_t,
        missing_in_base=missing_b,
        mismatched=mismatched,
        score=score,
        grade=_grade(score),
    )
