"""Integration tests for the envdiff CLI."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.cli import main


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_no_diff(runner, tmp_path):
    base = write(tmp_path, ".env.base", "A=1\nB=2\n")
    target = write(tmp_path, ".env.target", "A=1\nB=2\n")
    result = runner.invoke(main, [base, target])
    assert result.exit_code == 0
    assert "No differences" in result.output


def test_missing_key_reported(runner, tmp_path):
    base = write(tmp_path, ".env.base", "A=1\nB=2\n")
    target = write(tmp_path, ".env.target", "A=1\n")
    result = runner.invoke(main, [base, target])
    assert result.exit_code == 0
    assert "B" in result.output


def test_exit_code_on_diff(runner, tmp_path):
    base = write(tmp_path, ".env.base", "A=1\nB=2\n")
    target = write(tmp_path, ".env.target", "A=1\n")
    result = runner.invoke(main, [base, target, "--exit-code"])
    assert result.exit_code == 1


def test_no_exit_code_when_clean(runner, tmp_path):
    base = write(tmp_path, ".env.base", "A=1\n")
    target = write(tmp_path, ".env.target", "A=1\n")
    result = runner.invoke(main, [base, target, "--exit-code"])
    assert result.exit_code == 0


def test_show_values_flag(runner, tmp_path):
    base = write(tmp_path, ".env.base", "A=old\n")
    target = write(tmp_path, ".env.target", "A=new\n")
    result = runner.invoke(main, [base, target, "--show-values"])
    assert "old" in result.output
    assert "new" in result.output


def test_no_values_flag_skips_mismatch(runner, tmp_path):
    base = write(tmp_path, ".env.base", "A=old\n")
    target = write(tmp_path, ".env.target", "A=new\n")
    result = runner.invoke(main, [base, target, "--no-values"])
    assert "No differences" in result.output


def test_missing_file_error(runner, tmp_path):
    """Invoking with a non-existent file should exit with a non-zero code."""
    existing = write(tmp_path, ".env.base", "A=1\n")
    missing = str(tmp_path / "does_not_exist.env")
    result = runner.invoke(main, [existing, missing])
    assert result.exit_code != 0
