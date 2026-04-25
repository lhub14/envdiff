"""Tests for envdiff.env_diff_coverage."""
import pytest

from envdiff.env_diff_coverage import (
    CoverageResult,
    CoverageRow,
    compute_coverage,
)


def test_empty_envs_returns_empty_result():
    result = compute_coverage({})
    assert result.total_keys == 0
    assert result.fully_covered == 0
    assert result.overall_ratio == 1.0


def test_single_env_all_keys_fully_covered():
    envs = {"prod": {"HOST": "localhost", "PORT": "8080"}}
    result = compute_coverage(envs)
    assert result.total_keys == 2
    assert result.fully_covered == 2
    assert result.overall_ratio == 1.0


def test_missing_key_detected():
    envs = {
        "prod": {"HOST": "localhost", "PORT": "8080"},
        "staging": {"HOST": "staging.local"},
    }
    result = compute_coverage(envs)
    port_row = next(r for r in result.rows if r.key == "PORT")
    assert "staging" in port_row.missing_from
    assert "prod" in port_row.present_in
    assert not port_row.is_full


def test_coverage_ratio_computed_correctly():
    envs = {
        "a": {"KEY": "1"},
        "b": {"KEY": "2"},
        "c": {},
    }
    result = compute_coverage(envs)
    row = result.rows[0]
    assert row.key == "KEY"
    assert pytest.approx(row.coverage_ratio) == 2 / 3


def test_rows_sorted_alphabetically():
    envs = {"prod": {"ZEBRA": "z", "ALPHA": "a", "MIDDLE": "m"}}
    result = compute_coverage(envs)
    keys = [r.key for r in result.rows]
    assert keys == sorted(keys)


def test_overall_ratio_partial_coverage():
    envs = {
        "a": {"X": "1", "Y": "2"},
        "b": {"X": "1"},
    }
    result = compute_coverage(envs)
    # X is fully covered, Y is not => 1/2
    assert result.fully_covered == 1
    assert pytest.approx(result.overall_ratio) == 0.5


def test_file_names_preserved_in_result():
    envs = {"prod": {"A": "1"}, "dev": {"A": "1"}}
    result = compute_coverage(envs)
    assert set(result.file_names) == {"prod", "dev"}


def test_all_missing_from_one_file():
    envs = {
        "base": {"A": "1", "B": "2", "C": "3"},
        "empty": {},
    }
    result = compute_coverage(envs)
    assert result.fully_covered == 0
    for row in result.rows:
        assert "empty" in row.missing_from
