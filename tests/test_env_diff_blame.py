"""Tests for env_diff_blame and blame_formatter."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from envdiff.comparator import DiffResult
from envdiff.env_diff_blame import BlameEntry, BlameResult, blame_diff
from envdiff.blame_formatter import format_blame_result


def _diff(
    missing_in_target=None,
    missing_in_base=None,
    mismatched=None,
) -> DiffResult:
    return DiffResult(
        missing_in_target=missing_in_target or [],
        missing_in_base=missing_in_base or [],
        mismatched=mismatched or {},
    )


def test_blame_diff_no_differences(tmp_path):
    base = tmp_path / ".env.base"
    target = tmp_path / ".env.target"
    base.write_text("")
    target.write_text("")
    result = blame_diff(_diff(), base, target)
    assert result.entries == []


def test_blame_diff_entries_created(tmp_path):
    base = tmp_path / ".env.base"
    target = tmp_path / ".env.target"
    base.write_text("FOO=1\n")
    target.write_text("BAR=2\n")

    diff = _diff(missing_in_target=["FOO"], missing_in_base=["BAR"])

    with patch("envdiff.env_diff_blame._git_blame_key", return_value=("Alice", "abc1234")):
        result = blame_diff(diff, base, target)

    assert len(result.entries) == 2
    keys = {e.key for e in result.entries}
    assert keys == {"FOO", "BAR"}


def test_blame_diff_mismatch_entry(tmp_path):
    base = tmp_path / ".env"
    target = tmp_path / ".env.prod"
    base.write_text("KEY=a\n")
    target.write_text("KEY=b\n")

    diff = _diff(mismatched={"KEY": ("a", "b")})

    with patch("envdiff.env_diff_blame._git_blame_key", return_value=(None, None)):
        result = blame_diff(diff, base, target)

    assert len(result.entries) == 1
    assert result.entries[0].kind == "mismatch"
    assert result.entries[0].author is None


def test_git_blame_key_subprocess_failure(tmp_path):
    from envdiff.env_diff_blame import _git_blame_key
    import subprocess

    p = tmp_path / ".env"
    p.write_text("X=1\n")

    with patch("subprocess.check_output", side_effect=subprocess.CalledProcessError(128, "git")):
        author, commit = _git_blame_key(p, "X")

    assert author is None
    assert commit is None


def test_format_no_entries():
    result = BlameResult(entries=[])
    out = format_blame_result(result, colour=False)
    assert "No differences" in out


def test_format_with_entries():
    result = BlameResult(entries=[
        BlameEntry(key="DB_URL", kind="missing_in_target", author="Bob", commit="deadbee"),
    ])
    out = format_blame_result(result, colour=False)
    assert "DB_URL" in out
    assert "missing in target" in out
    assert "Bob" in out
    assert "deadbee" in out


def test_format_no_author():
    result = BlameResult(entries=[
        BlameEntry(key="SECRET", kind="mismatch", author=None, commit=None),
    ])
    out = format_blame_result(result, colour=False)
    assert "SECRET" in out
    assert "value mismatch" in out
