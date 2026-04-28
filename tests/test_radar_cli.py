"""Tests for envdiff.radar_cli"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.radar_cli import radar_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_identical_files_exit_0(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\nB=2\n")
    target = write(tmp_path, "target.env", "A=1\nB=2\n")
    result = runner.invoke(radar_cmd, [base, target])
    assert result.exit_code == 0


def test_missing_key_exits_1(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\nB=2\n")
    target = write(tmp_path, "target.env", "A=1\n")
    result = runner.invoke(radar_cmd, [base, target])
    assert result.exit_code == 1


def test_json_format_is_valid(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\n")
    target = write(tmp_path, "target.env", "A=1\n")
    result = runner.invoke(radar_cmd, ["--format", "json", base, target])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "base" in data
    assert "entries" in data
    assert len(data["entries"]) == 1


def test_json_entry_has_axes(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\nB=2\n")
    target = write(tmp_path, "target.env", "A=1\nB=2\n")
    result = runner.invoke(radar_cmd, ["--format", "json", base, target])
    data = json.loads(result.output)
    axes = data["entries"][0]["axes"]
    axis_names = {a["name"] for a in axes}
    assert "coverage" in axis_names
    assert "consistency" in axis_names


def test_multiple_targets_in_output(runner, tmp_path):
    base = write(tmp_path, "base.env", "X=1\n")
    t1 = write(tmp_path, "t1.env", "X=1\n")
    t2 = write(tmp_path, "t2.env", "X=1\n")
    result = runner.invoke(radar_cmd, [base, t1, t2])
    assert result.exit_code == 0
    assert "t1.env" in result.output
    assert "t2.env" in result.output
