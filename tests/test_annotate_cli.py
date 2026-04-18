"""Tests for the annotate CLI command."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.annotate_cli import annotate_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_no_diff_stdout(runner, tmp_path):
    base = write(tmp_path, "base.env", "KEY=val\n")
    target = write(tmp_path, "target.env", "KEY=val\n")
    result = runner.invoke(annotate_cmd, [str(base), str(target)])
    assert result.exit_code == 0
    assert "KEY=val" in result.output


def test_missing_key_annotated(runner, tmp_path):
    base = write(tmp_path, "base.env", "KEY=val\nGONE=x\n")
    target = write(tmp_path, "target.env", "KEY=val\n")
    result = runner.invoke(annotate_cmd, [str(base), str(target)])
    assert result.exit_code == 0
    assert "MISSING" in result.output


def test_output_file_written(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\n")
    target = write(tmp_path, "target.env", "A=1\n")
    out = tmp_path / "annotated.env"
    result = runner.invoke(annotate_cmd, [str(base), str(target), "-o", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_bad_base_file_exits(runner, tmp_path):
    target = write(tmp_path, "target.env", "A=1\n")
    result = runner.invoke(annotate_cmd, ["nonexistent.env", str(target)])
    assert result.exit_code != 0


def test_no_values_flag_suppresses_mismatch(runner, tmp_path):
    base = write(tmp_path, "base.env", "KEY=old\n")
    target = write(tmp_path, "target.env", "KEY=new\n")
    result = runner.invoke(annotate_cmd, [str(base), str(target), "--no-values"])
    assert result.exit_code == 0
    assert "MISMATCH" not in result.output
