"""Tests for envdiff.ignore."""

import pytest
from pathlib import Path

from envdiff.ignore import load_ignore_file, build_ignore_matcher, IgnoreParseError


def write_ignore(tmp_path: Path, content: str) -> Path:
    f = tmp_path / ".envdiffignore"
    f.write_text(content)
    return f


def test_empty_file_returns_empty_set(tmp_path):
    f = write_ignore(tmp_path, "")
    assert load_ignore_file(f) == set()


def test_comments_and_blanks_ignored(tmp_path):
    f = write_ignore(tmp_path, "# comment\n\nSECRET_KEY\n")
    assert load_ignore_file(f) == {"SECRET_KEY"}


def test_multiple_keys(tmp_path):
    f = write_ignore(tmp_path, "FOO\nBAR\nBAZ\n")
    assert load_ignore_file(f) == {"FOO", "BAR", "BAZ"}


def test_missing_file_returns_empty_set(tmp_path):
    result = load_ignore_file(tmp_path / "nonexistent")
    assert result == set()


def test_invalid_pattern_raises(tmp_path):
    f = write_ignore(tmp_path, "INVALID KEY")
    with pytest.raises(IgnoreParseError, match="Invalid pattern"):
        load_ignore_file(f)


def test_wildcard_pattern(tmp_path):
    f = write_ignore(tmp_path, "AWS_*\n")
    patterns = load_ignore_file(f)
    matcher = build_ignore_matcher(patterns)
    assert matcher("AWS_SECRET")
    assert matcher("AWS_ACCESS_KEY_ID")
    assert not matcher("DATABASE_URL")


def test_exact_match(tmp_path):
    f = write_ignore(tmp_path, "SECRET_KEY\n")
    patterns = load_ignore_file(f)
    matcher = build_ignore_matcher(patterns)
    assert matcher("SECRET_KEY")
    assert not matcher("SECRET_KEY_EXTRA")


def test_empty_patterns_never_ignores():
    matcher = build_ignore_matcher(set())
    assert not matcher("ANYTHING")
