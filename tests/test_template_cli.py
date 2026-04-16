"""Tests for the template CLI command."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.template_cli import template_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_stdout_output(runner: CliRunner, tmp_path: Path):
    p = write(tmp_path, ".env", "FOO=bar\nAPI_KEY=secret\n")
    result = runner.invoke(template_cmd, [str(p)])
    assert result.exit_code == 0
    assert "FOO=" in result.output
    assert "bar" not in result.output


def test_include_values_flag(runner: CliRunner, tmp_path: Path):
    p = write(tmp_path, ".env", "APP_NAME=myapp\nDB_PASSWORD=hidden\n")
    result = runner.invoke(template_cmd, [str(p), "--include-values"])
    assert result.exit_code == 0
    assert "APP_NAME=myapp" in result.output
    assert "hidden" not in result.output


def test_placeholder_option(runner: CliRunner, tmp_path: Path):
    p = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(template_cmd, [str(p), "--placeholder", "FILL_ME"])
    assert result.exit_code == 0
    assert "FOO=FILL_ME" in result.output


def test_output_file(runner: CliRunner, tmp_path: Path):
    p = write(tmp_path, ".env", "FOO=bar\n")
    dest = tmp_path / "out" / ".env.template"
    result = runner.invoke(template_cmd, [str(p), "--output", str(dest)])
    assert result.exit_code == 0
    assert dest.exists()
    assert "FOO=" in dest.read_text()


def test_bad_env_file_exits_2(runner: CliRunner, tmp_path: Path):
    p = write(tmp_path, ".env", "===bad===\n")
    result = runner.invoke(template_cmd, [str(p)])
    assert result.exit_code == 2
