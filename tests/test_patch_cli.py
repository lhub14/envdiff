"""Tests for envdiff.patch_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.patch_cli import patch_group


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_generate_no_diff_stdout(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\nB=2\n")
    target = write(tmp_path, "target.env", "A=1\nB=2\n")
    result = runner.invoke(patch_group, ["generate", str(base), str(target)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["operations"] == []


def test_generate_with_diff_stdout(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\n")
    target = write(tmp_path, "target.env", "A=2\nB=3\n")
    result = runner.invoke(patch_group, ["generate", str(base), str(target)])
    assert result.exit_code == 0
    data = json.loads(result.output)
    ops = {o["key"]: o for o in data["operations"]}
    assert ops["A"]["op"] == "change"
    assert ops["B"]["op"] == "add"


def test_generate_writes_to_file(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\n")
    target = write(tmp_path, "target.env", "A=2\n")
    out = tmp_path / "out.patch"
    result = runner.invoke(patch_group, ["generate", str(base), str(target), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert len(data["operations"]) == 1


def test_apply_patch_stdout(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\n")
    target = write(tmp_path, "target.env", "A=2\nB=3\n")
    patch_file = tmp_path / "diff.patch"
    runner.invoke(patch_group, ["generate", str(base), str(target), "-o", str(patch_file)])

    result = runner.invoke(patch_group, ["apply", str(base), str(patch_file)])
    assert result.exit_code == 0
    assert "A=2" in result.output
    assert "B=3" in result.output


def test_apply_writes_to_file(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\n")
    target = write(tmp_path, "target.env", "A=99\n")
    patch_file = tmp_path / "diff.patch"
    runner.invoke(patch_group, ["generate", str(base), str(target), "-o", str(patch_file)])
    out = tmp_path / "patched.env"
    result = runner.invoke(patch_group, ["apply", str(base), str(patch_file), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "A=99" in out.read_text()


def test_apply_bad_patch_file_exits(runner, tmp_path):
    env = write(tmp_path, "base.env", "A=1\n")
    bad = write(tmp_path, "bad.patch", "not json")
    result = runner.invoke(patch_group, ["apply", str(env), str(bad)])
    assert result.exit_code != 0
