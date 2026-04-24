"""Tests for envdiff.env_pivot and envdiff.pivot_formatter."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envdiff.env_pivot import pivot_envs, PivotRow
from envdiff.pivot_formatter import format_pivot
from envdiff.pivot_cli import pivot_cmd


# ---------------------------------------------------------------------------
# pivot_envs
# ---------------------------------------------------------------------------

def test_empty_envs_returns_empty_rows():
    result = pivot_envs({"a.env": {}, "b.env": {}})
    assert result.rows == []
    assert not result.has_gaps
    assert not result.has_mismatches


def test_uniform_key_present_in_all():
    envs = {"a.env": {"PORT": "8080"}, "b.env": {"PORT": "8080"}}
    result = pivot_envs(envs)
    assert len(result.rows) == 1
    row = result.rows[0]
    assert row.key == "PORT"
    assert row.is_uniform
    assert row.is_complete


def test_missing_key_detected():
    envs = {"a.env": {"PORT": "8080"}, "b.env": {}}
    result = pivot_envs(envs)
    assert result.has_gaps
    row = result.rows[0]
    assert not row.is_complete
    assert row.values["b.env"] is None


def test_mismatch_detected():
    envs = {"a.env": {"PORT": "8080"}, "b.env": {"PORT": "9090"}}
    result = pivot_envs(envs)
    assert result.has_mismatches
    row = result.rows[0]
    assert not row.is_uniform
    assert row.is_complete


def test_rows_sorted_alphabetically():
    envs = {"a.env": {"ZEBRA": "1", "ALPHA": "2"}, "b.env": {"ALPHA": "2", "ZEBRA": "1"}}
    result = pivot_envs(envs)
    keys = [r.key for r in result.rows]
    assert keys == sorted(keys)


def test_filenames_order_preserved():
    envs = {"z.env": {"K": "1"}, "a.env": {"K": "1"}}
    result = pivot_envs(envs)
    assert result.filenames == ["z.env", "a.env"]


# ---------------------------------------------------------------------------
# format_pivot
# ---------------------------------------------------------------------------

def test_format_no_rows():
    from envdiff.env_pivot import PivotResult
    result = PivotResult(filenames=["a.env"])
    assert "No keys" in format_pivot(result, colour=False)


def test_format_includes_filenames():
    envs = {"prod.env": {"DB": "x"}, "dev.env": {"DB": "y"}}
    result = pivot_envs(envs)
    output = format_pivot(result, colour=False)
    assert "prod.env" in output
    assert "dev.env" in output


def test_format_shows_missing_label():
    envs = {"a.env": {"KEY": "val"}, "b.env": {}}
    result = pivot_envs(envs)
    output = format_pivot(result, colour=False)
    assert "(missing)" in output


# ---------------------------------------------------------------------------
# pivot_cli
# ---------------------------------------------------------------------------

@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_pivot_no_diff_exits_0(runner, tmp_path):
    a = write(tmp_path, "a.env", "PORT=8080\n")
    b = write(tmp_path, "b.env", "PORT=8080\n")
    result = runner.invoke(pivot_cmd, [a, b, "--no-colour"])
    assert result.exit_code == 0


def test_pivot_gap_exits_1(runner, tmp_path):
    a = write(tmp_path, "a.env", "PORT=8080\n")
    b = write(tmp_path, "b.env", "")
    result = runner.invoke(pivot_cmd, [a, b, "--no-colour"])
    assert result.exit_code == 1


def test_pivot_mismatch_exits_1(runner, tmp_path):
    a = write(tmp_path, "a.env", "PORT=8080\n")
    b = write(tmp_path, "b.env", "PORT=9090\n")
    result = runner.invoke(pivot_cmd, [a, b, "--no-colour"])
    assert result.exit_code == 1


def test_pivot_bad_file_exits_2(runner, tmp_path):
    a = write(tmp_path, "a.env", "PORT=8080\n")
    result = runner.invoke(pivot_cmd, [a, "/nonexistent/path.env", "--no-colour"])
    assert result.exit_code == 2


def test_gaps_only_flag_filters(runner, tmp_path):
    a = write(tmp_path, "a.env", "PORT=8080\nDEBUG=true\n")
    b = write(tmp_path, "b.env", "PORT=8080\n")
    result = runner.invoke(pivot_cmd, [a, b, "--no-colour", "--gaps-only"])
    assert "DEBUG" in result.output
    assert "PORT" not in result.output
