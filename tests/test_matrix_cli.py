"""Tests for the matrix CLI command."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.matrix_cli import matrix_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_all_present_exits_0(runner, tmp_path):
    a = write(tmp_path, "a.env", "PORT=8080\nDEBUG=true\n")
    b = write(tmp_path, "b.env", "PORT=8080\nDEBUG=true\n")
    result = runner.invoke(matrix_cmd, [a, b])
    assert result.exit_code == 0


def test_missing_key_exits_1(runner, tmp_path):
    a = write(tmp_path, "a.env", "PORT=8080\nSECRET=abc\n")
    b = write(tmp_path, "b.env", "PORT=8080\n")
    result = runner.invoke(matrix_cmd, [a, b])
    assert result.exit_code == 1
    assert "MISSING" in result.output


def test_mismatch_exits_1(runner, tmp_path):
    a = write(tmp_path, "a.env", "PORT=80\n")
    b = write(tmp_path, "b.env", "PORT=3000\n")
    result = runner.invoke(matrix_cmd, [a, b])
    assert result.exit_code == 1
    assert "MISMATCH" in result.output


def test_json_output_structure(runner, tmp_path):
    a = write(tmp_path, "a.env", "KEY=val\n")
    b = write(tmp_path, "b.env", "KEY=val\n")
    result = runner.invoke(matrix_cmd, ["--json", a, b])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "env_names" in data
    assert "rows" in data
    assert data["rows"][0]["key"] == "KEY"


def test_gaps_only_filters_rows(runner, tmp_path):
    a = write(tmp_path, "a.env", "SHARED=1\nONLY_A=2\n")
    b = write(tmp_path, "b.env", "SHARED=1\n")
    result = runner.invoke(matrix_cmd, ["--gaps-only", a, b])
    assert "ONLY_A" in result.output
    assert "SHARED" not in result.output


def test_bad_file_exits_2(runner, tmp_path):
    good = write(tmp_path, "good.env", "K=1\n")
    result = runner.invoke(matrix_cmd, [good, "/nonexistent/path.env"])
    assert result.exit_code == 2
