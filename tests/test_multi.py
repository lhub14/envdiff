"""Tests for envdiff.multi module."""
from pathlib import Path
import pytest

from envdiff.multi import compare_many, MultiDiffResult


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_no_differences(tmp_path):
    base = write_env(tmp_path, "base.env", "KEY=val\nFOO=bar\n")
    t1 = write_env(tmp_path, "t1.env", "KEY=val\nFOO=bar\n")
    result = compare_many(base, [t1])
    assert not result.any_differences()


def test_missing_key_in_target(tmp_path):
    base = write_env(tmp_path, "base.env", "KEY=val\nEXTRA=x\n")
    t1 = write_env(tmp_path, "t1.env", "KEY=val\n")
    result = compare_many(base, [t1])
    assert result.any_differences()
    diff = result.results[str(t1)]
    assert "EXTRA" in diff.missing_in_target


def test_multiple_targets(tmp_path):
    base = write_env(tmp_path, "base.env", "A=1\nB=2\n")
    t1 = write_env(tmp_path, "t1.env", "A=1\nB=2\n")
    t2 = write_env(tmp_path, "t2.env", "A=1\n")
    result = compare_many(base, [t1, t2])
    assert len(result.results) == 2
    from envdiff.comparator import has_differences
    assert not has_differences(result.results[str(t1)])
    assert has_differences(result.results[str(t2)])


def test_ignore_keys(tmp_path):
    base = write_env(tmp_path, "base.env", "KEY=val\nSECRET=s\n")
    t1 = write_env(tmp_path, "t1.env", "KEY=val\n")
    result = compare_many(base, [t1], ignore_keys=frozenset({"SECRET"}))
    assert not result.any_differences()


def test_value_mismatch(tmp_path):
    base = write_env(tmp_path, "base.env", "KEY=val\n")
    t1 = write_env(tmp_path, "t1.env", "KEY=other\n")
    result = compare_many(base, [t1], check_values=True)
    diff = result.results[str(t1)]
    assert "KEY" in diff.value_mismatches
