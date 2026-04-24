"""Tests for envdiff.env_diff_report_card."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from envdiff.env_diff_report_card import (
    ReportCard,
    build_report_card,
    report_card_to_json,
)


def _score(value: float):
    s = MagicMock()
    s.score = value
    s.grade = "A" if value >= 90 else "B"
    return s


def _lint(errors: int = 0, warnings: int = 0):
    issues = []
    for _ in range(errors):
        i = MagicMock()
        i.severity = "error"
        issues.append(i)
    for _ in range(warnings):
        i = MagicMock()
        i.severity = "warning"
        issues.append(i)
    lr = MagicMock()
    lr.issues = issues
    return lr


def _health(passed: bool, status: str = "PASS"):
    h = MagicMock()
    h.passed = passed
    h.status = status
    return h


def _drift(added=(), removed=(), changed=()):
    d = MagicMock()
    d.added = set(added)
    d.removed = set(removed)
    d.changed = set(changed)
    return d


def test_grade_a_on_perfect_score():
    card = build_report_card(_score(100), _lint(), None, _health(True))
    assert card.grade == "A"


def test_grade_b():
    card = build_report_card(_score(88), _lint(), None, _health(True))
    assert card.grade == "B"


def test_grade_f_on_low_score():
    card = build_report_card(_score(30), _lint(), None, _health(False, "FAIL"))
    assert card.grade == "F"


def test_passed_requires_health_and_grade():
    card = build_report_card(_score(96), _lint(), None, _health(True))
    assert card.passed is True


def test_failed_when_health_fails():
    card = build_report_card(_score(98), _lint(), None, _health(False, "FAIL"))
    assert card.passed is False


def test_failed_when_grade_d():
    card = build_report_card(_score(55), _lint(), None, _health(True))
    assert card.passed is False


def test_json_includes_grade():
    card = build_report_card(_score(95), _lint(errors=1), None, _health(True))
    data = report_card_to_json(card)
    assert data["grade"] == "A"
    assert data["lint_errors"] == 1
    assert data["drift"] is None


def test_json_includes_drift_info():
    card = build_report_card(_score(90), _lint(), _drift(added=["NEW"]), _health(True))
    data = report_card_to_json(card)
    assert "NEW" in data["drift"]["added"]


def test_label_propagated():
    card = build_report_card(_score(100), _lint(), None, _health(True), label="prod")
    assert card.label == "prod"
    data = report_card_to_json(card)
    assert data["label"] == "prod"
