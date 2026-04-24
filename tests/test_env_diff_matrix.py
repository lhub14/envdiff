"""Tests for envdiff.env_diff_matrix."""
from __future__ import annotations

import pytest

from envdiff.env_diff_matrix import (
    build_matrix,
    MatrixCell,
    MatrixRow,
    MatrixResult,
)


def _envs(**kwargs):
    return {k: v for k, v in kwargs.items()}


def test_empty_envs_returns_empty_rows():
    result = build_matrix({})
    assert result.rows == []
    assert result.env_names == []


def test_single_env_all_keys_present():
    result = build_matrix({"prod": {"A": "1", "B": "2"}})
    assert len(result.rows) == 2
    assert all(r.is_complete for r in result.rows)


def test_missing_key_detected():
    envs = {"prod": {"A": "1", "B": "2"}, "dev": {"A": "1"}}
    result = build_matrix(envs)
    b_row = next(r for r in result.rows if r.key == "B")
    assert not b_row.is_complete
    assert "dev" in b_row.missing_in


def test_uniform_key_all_same_value():
    envs = {"prod": {"PORT": "8080"}, "dev": {"PORT": "8080"}}
    result = build_matrix(envs)
    assert result.rows[0].is_uniform


def test_mismatch_detected():
    envs = {"prod": {"PORT": "80"}, "dev": {"PORT": "3000"}}
    result = build_matrix(envs)
    assert not result.rows[0].is_uniform
    assert result.has_mismatches


def test_has_gaps_true_when_key_missing():
    envs = {"a": {"X": "1"}, "b": {}}
    result = build_matrix(envs)
    assert result.has_gaps


def test_has_gaps_false_when_all_present():
    envs = {"a": {"X": "1"}, "b": {"X": "2"}}
    result = build_matrix(envs)
    assert not result.has_gaps


def test_rows_sorted_alphabetically():
    envs = {"e": {"Z": "1", "A": "2", "M": "3"}}
    result = build_matrix(envs)
    keys = [r.key for r in result.rows]
    assert keys == sorted(keys)


def test_env_names_order_preserved():
    envs = {"prod": {"K": "1"}, "staging": {"K": "1"}, "dev": {"K": "1"}}
    result = build_matrix(envs)
    assert result.env_names == ["prod", "staging", "dev"]


def test_cell_present_false_for_missing_key():
    envs = {"a": {"ONLY_A": "yes"}, "b": {}}
    result = build_matrix(envs)
    row = result.rows[0]
    assert row.cells["a"].present is True
    assert row.cells["b"].present is False
    assert row.cells["b"].value is None
