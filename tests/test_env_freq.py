"""Tests for envdiff.env_freq."""
from __future__ import annotations

import pathlib

import pytest

from envdiff.env_freq import FreqResult, FreqRow, compute_freq


def write_env(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_empty_input_returns_empty_result():
    result = compute_freq([])
    assert result.rows == []
    assert result.total_files == 0


def test_single_file_all_keys_count_one(tmp_path):
    p = write_env(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    result = compute_freq([("a", p)])
    assert result.total_files == 1
    keys = {r.key for r in result.rows}
    assert keys == {"FOO", "BAR"}
    for row in result.rows:
        assert row.count == 1
        assert row.is_universal
        assert row.ratio == 1.0


def test_key_present_in_all_files_is_universal(tmp_path):
    p1 = write_env(tmp_path, "a.env", "SHARED=x\nONLY_A=1\n")
    p2 = write_env(tmp_path, "b.env", "SHARED=y\nONLY_B=2\n")
    result = compute_freq([("a", p1), ("b", p2)])
    assert "SHARED" in result.universal_keys
    assert "ONLY_A" not in result.universal_keys
    assert "ONLY_B" not in result.universal_keys


def test_key_in_one_file_is_unique(tmp_path):
    p1 = write_env(tmp_path, "a.env", "SHARED=1\nRARE=only\n")
    p2 = write_env(tmp_path, "b.env", "SHARED=1\n")
    result = compute_freq([("a", p1), ("b", p2)])
    assert "RARE" in result.unique_keys
    assert "SHARED" not in result.unique_keys


def test_rows_sorted_by_count_descending(tmp_path):
    p1 = write_env(tmp_path, "a.env", "A=1\nB=1\nC=1\n")
    p2 = write_env(tmp_path, "b.env", "A=2\nB=2\n")
    p3 = write_env(tmp_path, "c.env", "A=3\n")
    result = compute_freq([("a", p1), ("b", p2), ("c", p3)])
    counts = [r.count for r in result.rows]
    assert counts == sorted(counts, reverse=True)


def test_ratio_computed_correctly(tmp_path):
    p1 = write_env(tmp_path, "a.env", "X=1\n")
    p2 = write_env(tmp_path, "b.env", "X=2\n")
    p3 = write_env(tmp_path, "c.env", "Y=3\n")
    result = compute_freq([("a", p1), ("b", p2), ("c", p3)])
    row_x = next(r for r in result.rows if r.key == "X")
    assert pytest.approx(row_x.ratio) == 2 / 3


def test_files_list_contains_labels(tmp_path):
    p1 = write_env(tmp_path, "prod.env", "DB_URL=x\n")
    p2 = write_env(tmp_path, "staging.env", "DB_URL=y\n")
    result = compute_freq([("prod", p1), ("staging", p2)])
    row = next(r for r in result.rows if r.key == "DB_URL")
    assert "prod" in row.files
    assert "staging" in row.files


def test_missing_file_skipped_gracefully(tmp_path):
    p = write_env(tmp_path, "good.env", "KEY=val\n")
    result = compute_freq([("good", p), ("bad", "/nonexistent/missing.env")])
    # Only good file counted; total_files still reflects input length
    assert result.total_files == 2
    assert any(r.key == "KEY" for r in result.rows)
