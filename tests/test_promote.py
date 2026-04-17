"""Tests for envdiff.promote."""
from pathlib import Path

import pytest

from envdiff.promote import promote_env, has_changes


def write_env(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_promote_adds_missing_keys(tmp_path):
    src = write_env(tmp_path / "source.env", "A=1\nB=2\n")
    tgt = write_env(tmp_path / "target.env", "A=1\n")
    result = promote_env(src, tgt)
    assert "B" in result.added
    assert "A" in result.skipped
    assert result.output["B"] == "2"


def test_promote_skips_existing_keys_by_default(tmp_path):
    src = write_env(tmp_path / "source.env", "A=new\n")
    tgt = write_env(tmp_path / "target.env", "A=old\n")
    result = promote_env(src, tgt)
    assert "A" in result.skipped
    assert result.output["A"] == "old"
    assert not result.added


def test_promote_overwrite_replaces_existing(tmp_path):
    src = write_env(tmp_path / "source.env", "A=new\n")
    tgt = write_env(tmp_path / "target.env", "A=old\n")
    result = promote_env(src, tgt, overwrite=True)
    assert "A" in result.added
    assert result.output["A"] == "new"


def test_dry_run_does_not_write(tmp_path):
    src = write_env(tmp_path / "source.env", "A=1\nB=2\n")
    tgt = write_env(tmp_path / "target.env", "A=1\n")
    before = tgt.read_text()
    result = promote_env(src, tgt, dry_run=True)
    assert "B" in result.added
    assert tgt.read_text() == before


def test_has_changes_true(tmp_path):
    src = write_env(tmp_path / "source.env", "NEW=1\n")
    tgt = write_env(tmp_path / "target.env", "A=1\n")
    result = promote_env(src, tgt, dry_run=True)
    assert has_changes(result)


def test_has_changes_false(tmp_path):
    src = write_env(tmp_path / "source.env", "A=1\n")
    tgt = write_env(tmp_path / "target.env", "A=1\n")
    result = promote_env(src, tgt, dry_run=True)
    assert not has_changes(result)


def test_promote_writes_file(tmp_path):
    src = write_env(tmp_path / "source.env", "A=1\nB=hello world\n")
    tgt = write_env(tmp_path / "target.env", "A=1\n")
    promote_env(src, tgt)
    content = tgt.read_text()
    assert "B=\"hello world\"" in content
