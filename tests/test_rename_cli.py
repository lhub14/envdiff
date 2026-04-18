"""Tests for the rename CLI command."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

from envdiff.rename_cli import rename_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_no_candidates_exit_0(runner, tmp_path):
    base = write(tmp_path, "base.env", "DB_HOST=localhost\n")
    target = write(tmp_path, "target.env", "DB_HOST=localhost\n")
    result = runner.invoke(rename_cmd, [base, target])
    assert result.exit_code == 0
    assert "No rename candidates" in result.output


def test_rename_candidate_shown(runner, tmp_path):
    base = write(tmp_path, "base.env", "DATABASE_URL=x\n")
    target = write(tmp_path, "target.env", "DATABASE_URI=x\n")
    result = runner.invoke(rename_cmd, [base, target])
    assert result.exit_code == 0
    assert "DATABASE_URL" in result.output
    assert "DATABASE_URI" in result.output


def test_exit_code_flag(runner, tmp_path):
    base = write(tmp_path, "base.env", "DATABASE_URL=x\n")
    target = write(tmp_path, "target.env", "DATABASE_URI=x\n")
    result = runner.invoke(rename_cmd, ["--exit-code", base, target])
    assert result.exit_code == 1


def test_bad_file_exits_2(runner, tmp_path):
    base = write(tmp_path, "base.env", "123INVALID\n")
    target = write(tmp_path, "target.env", "KEY=val\n")
    result = runner.invoke(rename_cmd, [base, target])
    assert result.exit_code == 2


def test_threshold_option(runner, tmp_path):
    base = write(tmp_path, "base.env", "ABC=1\n")
    target = write(tmp_path, "target.env", "XYZ=1\n")
    result = runner.invoke(rename_cmd, ["--threshold", "0.99", base, target])
    assert result.exit_code == 0
    assert "No rename candidates" in result.output
