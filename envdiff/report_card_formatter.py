"""Terminal formatter for ReportCard."""
from __future__ import annotations

from envdiff.env_diff_report_card import ReportCard


def _bold(t: str) -> str:
    return f"\033[1m{t}\033[0m"


def _colour(grade: str, text: str) -> str:
    colours = {"A": "\033[32m", "B": "\033[32m", "C": "\033[33m", "D": "\033[31m", "F": "\033[31m"}
    reset = "\033[0m"
    return f"{colours.get(grade, '')}{text}{reset}"


def _red(t: str) -> str:
    return f"\033[31m{t}\033[0m"


def _green(t: str) -> str:
    return f"\033[32m{t}\033[0m"


def format_report_card(card: ReportCard, *, colour: bool = True) -> str:
    lines = []
    title = f"Report Card{': ' + card.label if card.label else ''}"
    lines.append(_bold(title) if colour else title)
    lines.append("-" * 40)

    grade_str = _colour(card.grade, card.grade) if colour else card.grade
    lines.append(f"  Grade   : {grade_str}")
    lines.append(f"  Score   : {card.score.score:.1f} / 100  ({card.score.grade})")

    errors = [i for i in card.lint.issues if i.severity == "error"]
    warnings = [i for i in card.lint.issues if i.severity == "warning"]
    lint_str = f"{len(errors)} error(s), {len(warnings)} warning(s)"
    lines.append(f"  Lint    : {lint_str}")

    health_str = card.health.status
    if colour:
        health_str = _green(health_str) if card.health.passed else _red(health_str)
    lines.append(f"  Health  : {health_str}")

    if card.drift is not None:
        total_drift = len(card.drift.added) + len(card.drift.removed) + len(card.drift.changed)
        lines.append(f"  Drift   : {total_drift} change(s) detected")
    else:
        lines.append("  Drift   : (not checked)")

    lines.append("-" * 40)
    verdict = "PASS" if card.passed else "FAIL"
    verdict_str = (_green(verdict) if card.passed else _red(verdict)) if colour else verdict
    lines.append(f"  Result  : {verdict_str}")
    return "\n".join(lines)
