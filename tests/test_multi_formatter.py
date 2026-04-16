"""Tests for envdiff.multi_formatter module."""
from pathlib import Path

from envdiff.multi import compare_many
from envdiff.multi_formatter import format_multi_diff


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_format_no_diff(tmp_path):
    base = write_env(tmp_path, "base.env", "KEY=val\n")
    t1 = write_env(tmp_path, "t1.env", "KEY=val\n")
    result = compare_many(base, [t1])
    output = format_multi_diff(result, color=False)
    assert "No differences" in output
    assert str(t1) in output


def test_format_with_diff(tmp_path):
    base = write_env(tmp_path, "base.env", "KEY=val\nMISSING=x\n")
    t1 = write_env(tmp_path, "t1.env", "KEY=val\n")
    result = compare_many(base, [t1])
    output = format_multi_diff(result, color=False)
    assert "MISSING" in output


def test_format_includes_base(tmp_path):
    base = write_env(tmp_path, "base.env", "A=1\n")
    t1 = write_env(tmp_path, "t1.env", "A=1\n")
    result = compare_many(base, [t1])
    output = format_multi_diff(result, color=False)
    assert str(base) in output


def test_multiple_targets_sections(tmp_path):
    base = write_env(tmp_path, "base.env", "A=1\n")
    t1 = write_env(tmp_path, "t1.env", "A=1\n")
    t2 = write_env(tmp_path, "t2.env", "A=1\n")
    result = compare_many(base, [t1, t2])
    output = format_multi_diff(result, color=False)
    assert str(t1) in output
    assert str(t2) in output
