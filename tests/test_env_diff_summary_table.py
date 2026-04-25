"""Tests for envdiff.env_diff_summary_table."""
import pytest
from envdiff.env_diff_summary_table import (
    build_summary_table,
    SummaryTableResult,
    SummaryTableRow,
)


def _envs(**kwargs):
    return {k: v for k, v in kwargs.items()}


def test_empty_envs_returns_empty_result():
    result = build_summary_table({})
    assert result.total_keys == 0
    assert result.filenames == []


def test_single_env_all_keys_uniform():
    result = build_summary_table({"a.env": {"HOST": "localhost", "PORT": "5432"}})
    assert result.total_keys == 2
    assert result.uniform_keys == 2
    assert result.incomplete_keys == 0
    assert result.mismatched_keys == 0


def test_missing_key_detected():
    result = build_summary_table({
        "base.env": {"HOST": "localhost", "PORT": "5432"},
        "prod.env": {"HOST": "prod-host"},
    })
    incomplete = [r for r in result.rows if not r.is_complete]
    assert len(incomplete) == 1
    assert incomplete[0].key == "PORT"
    assert "prod.env" in incomplete[0].missing_in


def test_mismatch_detected():
    result = build_summary_table({
        "base.env": {"HOST": "localhost"},
        "prod.env": {"HOST": "prod-host"},
    })
    assert result.mismatched_keys == 1
    assert result.uniform_keys == 0


def test_rows_sorted_alphabetically():
    result = build_summary_table({
        "a.env": {"ZEBRA": "1", "ALPHA": "2", "MIDDLE": "3"},
    })
    keys = [r.key for r in result.rows]
    assert keys == sorted(keys)


def test_uniform_and_complete_key():
    result = build_summary_table({
        "a.env": {"DB": "postgres"},
        "b.env": {"DB": "postgres"},
    })
    row = result.rows[0]
    assert row.is_uniform
    assert row.is_complete
    assert row.missing_in == []


def test_incomplete_keys_count():
    result = build_summary_table({
        "a.env": {"X": "1", "Y": "2"},
        "b.env": {"X": "1"},
    })
    assert result.incomplete_keys == 1
    assert result.total_keys == 2


def test_filenames_preserved_in_order():
    envs = {"first.env": {"A": "1"}, "second.env": {"A": "1"}, "third.env": {"A": "1"}}
    result = build_summary_table(envs)
    assert result.filenames == ["first.env", "second.env", "third.env"]
