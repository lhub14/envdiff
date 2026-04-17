"""Tests for envdiff.diff_summary."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.diff_summary import DiffSummary, summarise, format_summary


def _result(missing_target=(), missing_base=(), mismatched=None):
    return DiffResult(
        missing_in_target=set(missing_target),
        missing_in_base=set(missing_base),
        mismatched=dict(mismatched or {}),
    )


def test_empty_results():
    summary = summarise({})
    assert summary.total_files == 0
    assert summary.clean
    assert summary.total_issues == 0


def test_no_differences():
    summary = summarise({"prod": _result()})
    assert summary.total_files == 1
    assert summary.files_with_diff == 0
    assert summary.clean


def test_missing_in_target_counted():
    summary = summarise({"prod": _result(missing_target=["FOO", "BAR"])})
    assert summary.total_missing_in_target == 2
    assert summary.files_with_diff == 1
    assert not summary.clean


def test_missing_in_base_counted():
    summary = summarise({"prod": _result(missing_base=["EXTRA"])})
    assert summary.total_missing_in_base == 1


def test_mismatched_counted():
    summary = summarise({"prod": _result(mismatched={"KEY": ("a", "b")})})
    assert summary.total_mismatched == 1
    assert summary.total_issues == 1


def test_multiple_files_aggregated():
    results = {
        "staging": _result(missing_target=["A"]),
        "prod": _result(mismatched={"B": ("x", "y")}, missing_base=["C"]),
    }
    summary = summarise(results)
    assert summary.total_files == 2
    assert summary.files_with_diff == 2
    assert summary.total_missing_in_target == 1
    assert summary.total_mismatched == 1
    assert summary.total_missing_in_base == 1
    assert summary.total_issues == 3


def test_per_file_populated():
    summary = summarise({"prod": _result(missing_target=["FOO"])})
    assert "prod" in summary.per_file
    assert summary.per_file["prod"]["missing_in_target"] == ["FOO"]
    assert summary.per_file["prod"]["issues"] == 1


def test_format_summary_ok():
    summary = summarise({"prod": _result()})
    text = format_summary(summary)
    assert "Status: OK" in text
    assert "Files compared : 1" in text


def test_format_summary_with_issues():
    summary = summarise({"prod": _result(missing_target=["X"])})
    text = format_summary(summary)
    assert "1 issue(s) found" in text
