"""Tests for envdiff.annotate."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.comparator import compare_envs
from envdiff.annotate import annotate_lines, write_annotated


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_clean_file_no_annotations(tmp_path):
    base = write_env(tmp_path, "base.env", "KEY=value\nOTHER=x\n")
    base_env = {"KEY": "value", "OTHER": "x"}
    target_env = {"KEY": "value", "OTHER": "x"}
    diff = compare_envs(base_env, target_env)
    lines = annotate_lines(base, diff)
    assert lines == ["KEY=value", "OTHER=x"]


def test_missing_in_target_annotated(tmp_path):
    base = write_env(tmp_path, "base.env", "KEY=value\nGONE=x\n")
    base_env = {"KEY": "value", "GONE": "x"}
    target_env = {"KEY": "value"}
    diff = compare_envs(base_env, target_env)
    lines = annotate_lines(base, diff, target_label="prod.env")
    assert any("MISSING in prod.env" in l for l in lines)


def test_mismatch_annotated(tmp_path):
    base = write_env(tmp_path, "base.env", "KEY=old\n")
    base_env = {"KEY": "old"}
    target_env = {"KEY": "new"}
    diff = compare_envs(base_env, target_env, check_values=True)
    lines = annotate_lines(base, diff)
    assert any("MISMATCH" in l for l in lines)


def test_comments_and_blanks_preserved(tmp_path):
    base = write_env(tmp_path, "base.env", "# comment\n\nKEY=val\n")
    diff = compare_envs({"KEY": "val"}, {"KEY": "val"})
    lines = annotate_lines(base, diff)
    assert lines[0] == "# comment"
    assert lines[1] == ""


def test_write_annotated_to_file(tmp_path):
    base = write_env(tmp_path, "base.env", "A=1\n")
    diff = compare_envs({"A": "1"}, {"A": "1"})
    out = tmp_path / "sub" / "out.env"
    write_annotated(base, diff, output_path=out)
    assert out.exists()
    assert "A=1" in out.read_text()


def test_write_annotated_returns_string(tmp_path):
    base = write_env(tmp_path, "base.env", "A=1\n")
    diff = compare_envs({"A": "1"}, {})
    content = write_annotated(base, diff)
    assert "MISSING" in content
