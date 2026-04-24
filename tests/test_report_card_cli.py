"""Integration tests for the report-card CLI command."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.report_card_cli import report_card_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_identical_files_exit_0(runner, tmp_path):
    base = write(tmp_path, "base.env", "PORT=8080\nDEBUG=false\n")
    target = write(tmp_path, "target.env", "PORT=8080\nDEBUG=false\n")
    result = runner.invoke(report_card_cmd, [base, target])
    assert result.exit_code == 0
    assert "PASS" in result.output


def test_missing_key_may_fail(runner, tmp_path):
    base = write(tmp_path, "base.env", "PORT=8080\nSECRET=abc\n")
    target = write(tmp_path, "target.env", "PORT=8080\n")
    result = runner.invoke(report_card_cmd, [base, target])
    # exit code 0 or 1 depending on score threshold; output must contain grade
    assert "Grade" in result.output


def test_json_format_is_valid(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\nB=2\n")
    target = write(tmp_path, "target.env", "A=1\nB=2\n")
    result = runner.invoke(report_card_cmd, [base, target, "--format", "json"])
    data = json.loads(result.output)
    assert "grade" in data
    assert "score" in data
    assert "passed" in data


def test_label_shown_in_output(runner, tmp_path):
    base = write(tmp_path, "base.env", "X=1\n")
    target = write(tmp_path, "target.env", "X=1\n")
    result = runner.invoke(report_card_cmd, [base, target, "--label", "staging"])
    assert "staging" in result.output


def test_bad_base_file_exits_2(runner, tmp_path):
    bad = write(tmp_path, "bad.env", "123INVALID\n")
    good = write(tmp_path, "good.env", "A=1\n")
    result = runner.invoke(report_card_cmd, [bad, good])
    assert result.exit_code == 2
