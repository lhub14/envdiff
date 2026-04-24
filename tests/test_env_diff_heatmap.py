"""Tests for envdiff.env_diff_heatmap."""
from __future__ import annotations

from envdiff.comparator import DiffResult
from envdiff.env_diff_heatmap import (
    HeatmapRow,
    build_heatmap,
    has_hot_keys,
)


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


def test_empty_diffs_returns_empty_result():
    result = build_heatmap([])
    assert result.rows == []
    assert result.total_comparisons == 0


def test_no_differences_returns_empty_rows():
    result = build_heatmap([_diff(), _diff()])
    assert result.rows == []
    assert result.total_comparisons == 2


def test_single_diff_missing_target():
    result = build_heatmap([_diff(missing_target=["FOO"])])
    assert len(result.rows) == 1
    assert result.rows[0].key == "FOO"
    assert result.rows[0].diff_count == 1
    assert result.rows[0].total == 1


def test_ratio_computed_correctly():
    diffs = [
        _diff(missing_target=["BAR"]),
        _diff(missing_target=["BAR"]),
        _diff(),
        _diff(),
    ]
    result = build_heatmap(diffs)
    row = result.rows[0]
    assert row.key == "BAR"
    assert row.ratio == 0.5


def test_heat_levels():
    assert HeatmapRow("K", 0, 10).heat == "cold"
    assert HeatmapRow("K", 3, 10).heat == "warm"
    assert HeatmapRow("K", 7, 10).heat == "hot"
    assert HeatmapRow("K", 10, 10).heat == "critical"


def test_rows_sorted_by_diff_count_descending():
    diffs = [
        _diff(missing_target=["A", "B"]),
        _diff(missing_target=["A"]),
    ]
    result = build_heatmap(diffs)
    keys = [r.key for r in result.rows]
    assert keys[0] == "A"
    assert keys[1] == "B"


def test_has_hot_keys_true():
    result = build_heatmap([
        _diff(missing_target=["X"]),
        _diff(missing_target=["X"]),
        _diff(missing_target=["X"]),
        _diff(missing_target=["X"]),
        _diff(missing_target=["X"]),
    ])
    assert has_hot_keys(result) is True


def test_has_hot_keys_false_when_no_diffs():
    result = build_heatmap([_diff(), _diff()])
    assert has_hot_keys(result) is False


def test_mismatch_counted():
    diffs = [_diff(mismatched={"PORT": ("8080", "9090")})]
    result = build_heatmap(diffs)
    assert result.rows[0].key == "PORT"
    assert result.rows[0].diff_count == 1
