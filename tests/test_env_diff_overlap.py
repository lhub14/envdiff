"""Tests for envdiff.env_diff_overlap and overlap_formatter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.env_diff_overlap import OverlapRow, OverlapResult, compute_overlap
from envdiff.overlap_cli import overlap_cmd
from envdiff.overlap_formatter import format_overlap_result


# ---------------------------------------------------------------------------
# compute_overlap
# ---------------------------------------------------------------------------

def test_empty_input_returns_empty_result():
    result = compute_overlap({})
    assert result.rows == []
    assert result.file_names == []


def test_single_file_all_keys_universal():
    result = compute_overlap({"a.env": {"FOO": "1", "BAR": "2"}})
    assert result.universal_keys == ["BAR", "FOO"]
    assert result.unique_keys == []   # unique requires exactly 1 of N>1
    assert result.partial_keys == []


def test_universal_key_present_in_all():
    envs = {"a.env": {"SHARED": "x", "ONLY_A": "1"}, "b.env": {"SHARED": "x"}}
    result = compute_overlap(envs)
    assert "SHARED" in result.universal_keys
    assert "ONLY_A" in result.unique_keys


def test_overlap_ratio_computed_correctly():
    envs = {"a.env": {"K": "1"}, "b.env": {"K": "2"}, "c.env": {}}
    result = compute_overlap(envs)
    row = next(r for r in result.rows if r.key == "K")
    assert abs(row.overlap_ratio - 2 / 3) < 1e-9


def test_rows_sorted_alphabetically():
    envs = {"a.env": {"ZEBRA": "z", "APPLE": "a"}}
    result = compute_overlap(envs)
    keys = [r.key for r in result.rows]
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# format_overlap_result
# ---------------------------------------------------------------------------

def test_format_no_keys_message():
    result = OverlapResult()
    assert format_overlap_result(result) == "No keys found."


def test_format_contains_key_name():
    envs = {"a.env": {"MY_KEY": "v"}, "b.env": {"MY_KEY": "v"}}
    result = compute_overlap(envs)
    text = format_overlap_result(result, colour=False)
    assert "MY_KEY" in text


def test_format_summary_counts():
    envs = {"a.env": {"SHARED": "1", "ONLY_A": "2"}, "b.env": {"SHARED": "1"}}
    result = compute_overlap(envs)
    text = format_overlap_result(result, colour=False)
    assert "Universal" in text
    assert "Unique" in text


# ---------------------------------------------------------------------------
# overlap_cmd CLI
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_all_universal_exits_0(runner, tmp_path):
    a = write(tmp_path, "a.env", "FOO=1\nBAR=2\n")
    b = write(tmp_path, "b.env", "FOO=1\nBAR=2\n")
    result = runner.invoke(overlap_cmd, [a, b])
    assert result.exit_code == 0


def test_unique_key_exits_1(runner, tmp_path):
    a = write(tmp_path, "a.env", "FOO=1\nONLY_A=x\n")
    b = write(tmp_path, "b.env", "FOO=1\n")
    result = runner.invoke(overlap_cmd, [a, b])
    assert result.exit_code == 1


def test_json_output_structure(runner, tmp_path):
    a = write(tmp_path, "a.env", "FOO=1\n")
    b = write(tmp_path, "b.env", "FOO=1\nBAR=2\n")
    result = runner.invoke(overlap_cmd, ["--format", "json", a, b])
    data = json.loads(result.output)
    assert "universal" in data
    assert "unique" in data
    assert "rows" in data
