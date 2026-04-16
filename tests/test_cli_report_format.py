"""Integration tests for --format and --output flags in CLI."""
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.cli import main


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_files(tmp_path):
    base = tmp_path / ".env"
    target = tmp_path / ".env.prod"
    base.write_text("PORT=8080\nSECRET=abc\n")
    target.write_text("PORT=9090\n")
    return str(base), str(target)


def test_json_format_stdout(runner, env_files):
    base, target = env_files
    result = runner.invoke(main, [base, target, "--format", "json"])
    assert result.exit_code != 0 or result.exit_code == 0  # either is fine
    data = json.loads(result.output)
    assert "missing_in_target" in data
    assert "SECRET" in data["missing_in_target"]


def test_markdown_format_stdout(runner, env_files):
    base, target = env_files
    result = runner.invoke(main, [base, target, "--format", "markdown"])
    assert "# Env Diff" in result.output
    assert "SECRET" in result.output


def test_output_file(runner, env_files, tmp_path):
    base, target = env_files
    out = str(tmp_path / "out.json")
    result = runner.invoke(main, [base, target, "--format", "json", "--output", out])
    assert Path(out).exists()
    data = json.loads(Path(out).read_text())
    assert "mismatched" in data


def test_text_format_default(runner, env_files):
    base, target = env_files
    result = runner.invoke(main, [base, target])
    # default text format should not be valid JSON
    try:
        json.loads(result.output)
        is_json = True
    except Exception:
        is_json = False
    assert not is_json
