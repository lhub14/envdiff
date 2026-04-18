"""Format a ScoreResult for terminal output."""
from __future__ import annotations

from envdiff.score import ScoreResult


def _colour(grade: str, text: str) -> str:
    codes = {"A": "\033[32m", "B": "\033[32m", "C": "\033[33m", "D": "\033[33m", "F": "\033[31m"}
    reset = "\033[0m"
    return f"{codes.get(grade, '')}{text}{reset}"


def format_score(result: ScoreResult, *, colour: bool = True) -> str:
    grade_str = f"[{result.grade}]" if not colour else _colour(result.grade, f"[{result.grade}]")
    lines = [
        f"Env health score: {result.score:.1f}/100  {grade_str}",
        f"  Total base keys : {result.total_keys}",
        f"  Missing in target: {result.missing_in_target}",
        f"  Extra in target  : {result.missing_in_base}",
        f"  Mismatched values: {result.mismatched}",
    ]
    return "\n".join(lines)
