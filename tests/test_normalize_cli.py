"""Tests for envdiff.normalize_cli."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.normalize_cli import normalize_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content, encoding="utf-8")
    return p


def test_clean_file_exits_0(runner, tmp_path):
    p = write(tmp_path, "KEY=value\n")
    result = runner.invoke(normalize_cmd, [str(p), "--no-colour"])
    assert result.exit_code == 0
    assert "normalized" in result.output


def test_dirty_file_shows_changes(runner, tmp_path):
    p = write(tmp_path, "KEY=hello world\n")
    result = runner.invoke(normalize_cmd, [str(p), "--no-colour"])
    assert result.exit_code == 0
    assert "KEY" in result.output


def test_write_flag_modifies_file(runner, tmp_path):
    p = write(tmp_path, "KEY=hello world\n")
    result = runner.invoke(normalize_cmd, [str(p), "--write", "--no-colour"])
    assert result.exit_code == 0
    assert '"hello world"' in p.read_text()


def test_check_flag_exits_1_when_dirty(runner, tmp_path):
    p = write(tmp_path, "KEY=hello world\n")
    result = runner.invoke(normalize_cmd, [str(p), "--check", "--no-colour"])
    assert result.exit_code == 1


def test_check_flag_exits_0_when_clean(runner, tmp_path):
    p = write(tmp_path, "KEY=value\n")
    result = runner.invoke(normalize_cmd, [str(p), "--check", "--no-colour"])
    assert result.exit_code == 0
