"""Tests for envdiff.env_diff_trend and envdiff.trend_formatter."""
from __future__ import annotations

import pytest

from envdiff.comparator import DiffResult
from envdiff.env_diff_trend import (
    TrendPoint,
    TrendResult,
    build_trend,
    has_trend_data,
    is_improving,
    is_degrading,
)
from envdiff.trend_formatter import format_trend_result


def _diff(
    missing_target: list[str] | None = None,
    missing_base: list[str] | None = None,
    mismatched: dict[str, tuple[str, str]] | None = None,
) -> DiffResult:
    return DiffResult(
        missing_in_target=missing_target or [],
        missing_in_base=missing_base or [],
        mismatched=mismatched or {},
    )


def test_empty_input_returns_empty_result():
    result = build_trend([])
    assert result.points == []
    assert not has_trend_data(result)


def test_single_point_built_correctly():
    d = _diff(missing_target=["A", "B"], mismatched={"C": ("x", "y")})
    result = build_trend([("v1", d)])
    assert len(result.points) == 1
    pt = result.points[0]
    assert pt.label == "v1"
    assert pt.missing_in_target == 2
    assert pt.missing_in_base == 0
    assert pt.mismatched == 1
    assert pt.total_issues == 3


def test_multiple_points_ordered():
    pairs = [
        ("v1", _diff(missing_target=["A", "B", "C"])),
        ("v2", _diff(missing_target=["A", "B"])),
        ("v3", _diff(missing_target=["A"])),
    ]
    result = build_trend(pairs)
    assert [p.label for p in result.points] == ["v1", "v2", "v3"]
    assert [p.total_issues for p in result.points] == [3, 2, 1]


def test_is_improving():
    result = build_trend([
        ("v1", _diff(missing_target=["A", "B"])),
        ("v2", _diff()),
    ])
    assert is_improving(result)
    assert not is_degrading(result)


def test_is_degrading():
    result = build_trend([
        ("v1", _diff()),
        ("v2", _diff(missing_target=["A", "B"])),
    ])
    assert is_degrading(result)
    assert not is_improving(result)


def test_stable_neither_improving_nor_degrading():
    result = build_trend([
        ("v1", _diff(missing_target=["A"])),
        ("v2", _diff(missing_target=["B"])),
    ])
    assert not is_improving(result)
    assert not is_degrading(result)


def test_single_point_not_improving_or_degrading():
    result = build_trend([("v1", _diff(missing_target=["A"]))])
    assert not is_improving(result)
    assert not is_degrading(result)


def test_format_no_data():
    out = format_trend_result(TrendResult(), colour=False)
    assert "No trend data" in out


def test_format_includes_labels():
    result = build_trend([
        ("sprint-1", _diff(missing_target=["A"])),
        ("sprint-2", _diff()),
    ])
    out = format_trend_result(result, colour=False)
    assert "sprint-1" in out
    assert "sprint-2" in out


def test_format_improving_label():
    result = build_trend([
        ("v1", _diff(missing_target=["A", "B"])),
        ("v2", _diff()),
    ])
    out = format_trend_result(result, colour=False)
    assert "improving" in out


def test_format_degrading_label():
    result = build_trend([
        ("v1", _diff()),
        ("v2", _diff(missing_target=["A", "B", "C"])),
    ])
    out = format_trend_result(result, colour=False)
    assert "degrading" in out
