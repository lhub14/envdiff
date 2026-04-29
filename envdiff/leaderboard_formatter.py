"""Format a LeaderboardResult for terminal output."""
from __future__ import annotations

from typing import List

from envdiff.env_diff_leaderboard import LeaderboardEntry, LeaderboardResult


def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


def _green(text: str) -> str:
    return f"\033[32m{text}\033[0m"


def _yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"


def _red(text: str) -> str:
    return f"\033[31m{text}\033[0m"


def _colour_grade(grade: str) -> str:
    if grade in ("A+", "A"):
        return _green(grade)
    if grade in ("B", "C"):
        return _yellow(grade)
    return _red(grade)


def _rank_label(index: int) -> str:
    medals = {0: "🥇", 1: "🥈", 2: "🥉"}
    return medals.get(index, f"#{index + 1}")


def format_leaderboard(result: LeaderboardResult, no_colour: bool = False) -> str:
    if not result.entries:
        return "No targets to rank."

    lines: List[str] = [
        _bold(f"Leaderboard — base: {result.base_name}"),
        "",
    ]

    header = f"  {'Rank':<5} {'Name':<30} {'Score':>6}  {'Grade':<6}  Issues"
    lines.append(header)
    lines.append("  " + "-" * 58)

    for idx, entry in enumerate(result.entries):
        rank = _rank_label(idx)
        grade = _colour_grade(entry.grade) if not no_colour else entry.grade
        issues = entry.total_issues
        issue_str = f"{issues} issue{'s' if issues != 1 else ''}"
        lines.append(
            f"  {rank:<5} {entry.name:<30} {entry.score:>5}%  {grade:<6}  {issue_str}"
        )

    return "\n".join(lines)
