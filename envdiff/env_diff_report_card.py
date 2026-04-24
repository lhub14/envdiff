"""Report card: aggregate health, score, lint, and drift into a single graded summary."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envdiff.score import ScoreResult
from envdiff.lint import LintResult
from envdiff.drift import DriftResult
from envdiff.health import HealthReport


@dataclass
class ReportCard:
    score: ScoreResult
    lint: LintResult
    drift: Optional[DriftResult]
    health: HealthReport
    label: str = ""

    @property
    def grade(self) -> str:
        s = self.score.score
        if s >= 95:
            return "A"
        if s >= 85:
            return "B"
        if s >= 70:
            return "C"
        if s >= 50:
            return "D"
        return "F"

    @property
    def passed(self) -> bool:
        return self.health.passed and self.grade not in ("D", "F")


def build_report_card(
    score: ScoreResult,
    lint: LintResult,
    drift: Optional[DriftResult],
    health: HealthReport,
    label: str = "",
) -> ReportCard:
    return ReportCard(score=score, lint=lint, drift=drift, health=health, label=label)


def report_card_to_json(card: ReportCard) -> dict:
    drift_info = None
    if card.drift is not None:
        drift_info = {
            "added": list(card.drift.added),
            "removed": list(card.drift.removed),
            "changed": list(card.drift.changed),
        }
    return {
        "label": card.label,
        "grade": card.grade,
        "passed": card.passed,
        "score": card.score.score,
        "lint_errors": len([i for i in card.lint.issues if i.severity == "error"]),
        "lint_warnings": len([i for i in card.lint.issues if i.severity == "warning"]),
        "health_status": card.health.status,
        "drift": drift_info,
    }
