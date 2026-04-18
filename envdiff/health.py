"""Health check: aggregate env file quality into a pass/warn/fail status."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envdiff.score import ScoreResult
from envdiff.lint import LintResult, has_issues, errors as lint_errors, warnings as lint_warnings


@dataclass
class HealthReport:
    status: str  # "pass" | "warn" | "fail"
    score: int
    grade: str
    error_count: int
    warning_count: int
    reasons: List[str] = field(default_factory=list)


def check_health(
    score_result: ScoreResult,
    lint_result: LintResult,
    score_threshold: int = 80,
) -> HealthReport:
    reasons: list[str] = []
    error_count = len(lint_errors(lint_result))
    warning_count = len(lint_warnings(lint_result))

    if error_count:
        reasons.append(f"{error_count} lint error(s) found")
    if warning_count:
        reasons.append(f"{warning_count} lint warning(s) found")
    if score_result.score < score_threshold:
        reasons.append(
            f"score {score_result.score} is below threshold {score_threshold}"
        )

    if error_count or score_result.score < score_threshold:
        status = "fail"
    elif warning_count:
        status = "warn"
    else:
        status = "pass"

    return HealthReport(
        status=status,
        score=score_result.score,
        grade=score_result.grade,
        error_count=error_count,
        warning_count=warning_count,
        reasons=reasons,
    )


def format_health(report: HealthReport) -> str:
    icon = {"pass": "✓", "warn": "!", "fail": "✗"}.get(report.status, "?")
    lines = [
        f"{icon} Health: {report.status.upper()}  "
        f"(score {report.score}/100, grade {report.grade})",
    ]
    if report.reasons:
        for r in report.reasons:
            lines.append(f"  - {r}")
    return "\n".join(lines)
