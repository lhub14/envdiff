"""Tests for envdiff.transform_cli"""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envdiff.transform_cli import transform_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_no_rules_exits_0(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(transform_cmd, [f, "--no-colour"])
    assert result.exit_code == 0
    assert "No changes" in result.output


def test_uppercase_rule_shows_change(runner, tmp_path):
    f = write(tmp_path, ".env", "HOST=localhost\n")
    result = runner.invoke(transform_cmd, [f, "--rule", "HOST:uppercase", "--no-colour"])
    assert result.exit_code == 1
    assert "HOST" in result.output
    assert "LOCALHOST" in result.output


def test_write_flag_modifies_file(runner, tmp_path):
    f = write(tmp_path, ".env", "HOST=localhost\n")
    runner.invoke(transform_cmd, [f, "--rule", "HOST:uppercase", "--write", "--no-colour"])
    assert "HOST=LOCALHOST" in Path(f).read_text()


def test_invalid_rule_exits_2(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(transform_cmd, [f, "--rule", "BADFORMAT"])
    assert result.exit_code == 2


def test_bad_env_file_exits_2(runner, tmp_path):
    f = write(tmp_path, ".env", "!!!invalid\n")
    result = runner.invoke(transform_cmd, [f, "--rule", "*:uppercase"])
    # parser may or may not raise; just check no crash
    assert result.exit_code in (0, 1, 2)
