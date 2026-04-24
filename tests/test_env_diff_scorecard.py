"""Tests for envdiff.env_diff_scorecard."""
from __future__ import annotations

from envdiff.comparator import DiffResult
from envdiff.env_diff_scorecard import (
    ScorecardRow,
    ScorecardResult,
    build_scorecard,
)
from envdiff.lint import LintResult, LintIssue
from envdiff.schema import SchemaResult


def _diff(
    missing_in_target=None,
    missing_in_base=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        missing_in_target=missing_in_target or [],
        missing_in_base=missing_in_base or [],
        mismatched=mismatched or {},
    )


def test_empty_diff_returns_empty_scorecard():
    result = build_scorecard(_diff())
    assert result.total == 0
    assert result.passing == 0
    assert result.failing == 0


def test_missing_in_target_creates_failing_row():
    result = build_scorecard(_diff(missing_in_target=["DB_HOST"]))
    assert result.total == 1
    row = result.rows[0]
    assert row.key == "DB_HOST"
    assert row.in_base is True
    assert row.in_target is False
    assert not row.ok


def test_missing_in_base_creates_failing_row():
    result = build_scorecard(_diff(missing_in_base=["SECRET_KEY"]))
    row = result.rows[0]
    assert row.in_base is False
    assert row.in_target is True
    assert not row.ok


def test_mismatch_creates_failing_row():
    result = build_scorecard(_diff(mismatched={"PORT": ("8080", "9090")}))
    row = result.rows[0]
    assert row.key == "PORT"
    assert row.values_match is False
    assert not row.ok


def test_lint_warnings_attached_to_row():
    diff = _diff(missing_in_target=["bad_key"])
    issue = LintIssue(key="bad_key", message="lowercase key", severity="warning")
    lint = LintResult(issues=[issue])
    result = build_scorecard(diff, lint=lint)
    row = result.rows[0]
    assert "lowercase key" in row.lint_warnings
    assert not row.ok


def test_schema_violations_attached_to_row():
    diff = _diff(missing_in_target=["API_KEY"])
    schema = SchemaResult(missing_required=["API_KEY"], invalid_pattern={})
    result = build_scorecard(diff, schema=schema)
    row = result.rows[0]
    assert any("missing required" in v for v in row.schema_violations)


def test_passing_and_failing_counts():
    diff = _diff(missing_in_target=["A"], missing_in_base=["B"])
    result = build_scorecard(diff)
    assert result.total == 2
    assert result.failing == 2
    assert result.passing == 0


def test_rows_sorted_alphabetically():
    diff = _diff(missing_in_target=["ZEBRA", "ALPHA", "MIDDLE"])
    result = build_scorecard(diff)
    keys = [r.key for r in result.rows]
    assert keys == sorted(keys)
