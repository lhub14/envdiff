"""Tests for envdiff.lint."""
from __future__ import annotations
import pytest
from pathlib import Path
from envdiff.lint import lint_env_file, LintResult


def write_env(tmp_path: Path, content: str) -> str:
    p = tmp_path / ".env"
    p.write_text(content)
    return str(p)


def test_clean_file(tmp_path):
    path = write_env(tmp_path, "FOO=bar\nBAR=baz\n")
    result = lint_env_file(path)
    assert not result.has_issues


def test_invalid_key(tmp_path):
    path = write_env(tmp_path, "123BAD=value\n")
    result = lint_env_file(path)
    errors = [i for i in result.issues if i.severity == "error"]
    assert any("Invalid key" in e.message for e in errors)


def test_lowercase_key_warns(tmp_path):
    path = write_env(tmp_path, "mykey=value\n")
    result = lint_env_file(path)
    warnings = result.warnings
    assert any("UPPER_SNAKE_CASE" in w.message for w in warnings)


def test_duplicate_key_warns(tmp_path):
    path = write_env(tmp_path, "FOO=first\nFOO=second\n")
    result = lint_env_file(path)
    assert any("Duplicate" in i.message for i in result.warnings)


def test_empty_value_warns(tmp_path):
    path = write_env(tmp_path, "FOO=\n")
    result = lint_env_file(path)
    assert any("Empty value" in i.message for i in result.warnings)


def test_no_equals_is_error(tmp_path):
    path = write_env(tmp_path, "NODIVIDER\n")
    result = lint_env_file(path)
    assert any(i.severity == "error" for i in result.issues)


def test_comments_and_blanks_ignored(tmp_path):
    path = write_env(tmp_path, "# comment\n\nFOO=bar\n")
    result = lint_env_file(path)
    assert not result.has_issues


def test_missing_file_returns_error():
    result = lint_env_file("/nonexistent/.env")
    assert result.has_issues
    assert result.errors[0].severity == "error"
    assert result.errors[0].line == 0
