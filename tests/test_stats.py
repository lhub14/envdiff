"""Tests for envdiff.stats and envdiff.stats_formatter."""
from __future__ import annotations

import pathlib
import pytest

from envdiff.stats import compute_stats
from envdiff.stats_formatter import format_stats


def write_env(tmp_path: pathlib.Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_total_keys(tmp_path):
    a = write_env(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = write_env(tmp_path, "b.env", "FOO=1\nBAZ=3\n")
    result = compute_stats([a, b])
    assert len(result.all_keys) == 3
    assert result.common_keys == ["FOO"]


def test_empty_values_counted(tmp_path):
    a = write_env(tmp_path, "a.env", "FOO=\nBAR=hello\n")
    result = compute_stats([a])
    assert result.files[0].empty_values == 1


def test_sensitive_keys_counted(tmp_path):
    a = write_env(tmp_path, "a.env", "SECRET_KEY=abc\nNAME=test\n")
    result = compute_stats([a])
    assert result.files[0].sensitive_keys == 1


def test_unique_keys_per_file(tmp_path):
    a = write_env(tmp_path, "a.env", "FOO=1\nONLY_A=x\n")
    b = write_env(tmp_path, "b.env", "FOO=1\nONLY_B=y\n")
    result = compute_stats([a, b])
    a_stats = next(f for f in result.files if f.file == a)
    b_stats = next(f for f in result.files if f.file == b)
    assert a_stats.unique_keys == ["ONLY_A"]
    assert b_stats.unique_keys == ["ONLY_B"]


def test_single_file(tmp_path):
    a = write_env(tmp_path, "a.env", "X=1\nY=2\n")
    result = compute_stats([a])
    assert result.common_keys == ["X", "Y"]
    assert result.files[0].unique_keys == []


def test_format_stats_contains_file_name(tmp_path):
    a = write_env(tmp_path, "prod.env", "FOO=1\n")
    result = compute_stats([a])
    output = format_stats(result, colour=False)
    assert "prod.env" in output
    assert "Total keys" in output


def test_format_stats_shows_unique_keys(tmp_path):
    a = write_env(tmp_path, "a.env", "ONLY_HERE=1\nSHARED=x\n")
    b = write_env(tmp_path, "b.env", "SHARED=x\n")
    result = compute_stats([a, b])
    output = format_stats(result, colour=False)
    assert "ONLY_HERE" in output
