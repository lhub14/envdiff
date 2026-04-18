"""Tests for envdiff.env_normalize."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.env_normalize import (
    NormalizeResult,
    has_changes,
    normalize_env,
    write_normalized,
)


def write_env(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content, encoding="utf-8")
    return p


def test_already_normalized(tmp_path):
    p = write_env(tmp_path, "KEY=value\nFOO=bar\n")
    result = normalize_env(p)
    assert not has_changes(result)
    assert result.duplicates_removed == []


def test_trailing_whitespace_detected(tmp_path):
    p = write_env(tmp_path, "KEY=value   \n")
    result = normalize_env(p)
    assert has_changes(result)


def test_value_with_space_gets_quoted(tmp_path):
    p = write_env(tmp_path, 'KEY=hello world\n')
    result = normalize_env(p)
    assert any("KEY" in k for k, _ in result.changes)
    assert any('"hello world"' in line for line in result.normalized_lines)


def test_duplicate_key_removed(tmp_path):
    p = write_env(tmp_path, "KEY=first\nKEY=second\n")
    result = normalize_env(p)
    assert "KEY" in result.duplicates_removed
    assert sum(1 for l in result.normalized_lines if l.startswith("KEY=")) == 1


def test_comments_and_blanks_preserved(tmp_path):
    p = write_env(tmp_path, "# comment\n\nKEY=val\n")
    result = normalize_env(p)
    assert "# comment" in result.normalized_lines
    assert "" in result.normalized_lines


def test_write_normalized(tmp_path):
    p = write_env(tmp_path, "KEY=hello world\n")
    result = normalize_env(p)
    write_normalized(result, p)
    content = p.read_text(encoding="utf-8")
    assert '"hello world"' in content


def test_has_changes_false_when_clean(tmp_path):
    p = write_env(tmp_path, "A=1\nB=2\n")
    result = normalize_env(p)
    assert not has_changes(result)


def test_existing_quotes_normalized(tmp_path):
    # single-quoted value should be re-emitted without quotes if no spaces
    p = write_env(tmp_path, "KEY='simple'\n")
    result = normalize_env(p)
    assert any("KEY=simple" == l for l in result.normalized_lines)
