"""Tests for envdiff.parser module."""

import pytest
from pathlib import Path

from envdiff.parser import parse_env_file, EnvParseError


def write_env(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content, encoding="utf-8")
    return p


def test_basic_key_value(tmp_path):
    p = write_env(tmp_path, "KEY=value\nANOTHER=123\n")
    result = parse_env_file(p)
    assert result == {"KEY": "value", "ANOTHER": "123"}


def test_quoted_values(tmp_path):
    p = write_env(tmp_path, 'DB_URL="postgres://localhost/db"\nSECRET=\'abc123\'\n')
    result = parse_env_file(p)
    assert result["DB_URL"] == "postgres://localhost/db"
    assert result["SECRET"] == "abc123"


def test_empty_value(tmp_path):
    p = write_env(tmp_path, "EMPTY=\n")
    result = parse_env_file(p)
    assert result["EMPTY"] is None


def test_comments_and_blank_lines(tmp_path):
    content = "\n# This is a comment\nKEY=val\n\n"
    p = write_env(tmp_path, content)
    result = parse_env_file(p)
    assert result == {"KEY": "val"}


def test_inline_comment(tmp_path):
    p = write_env(tmp_path, "PORT=8080 # http port\n")
    result = parse_env_file(p)
    assert result["PORT"] == "8080"


def test_file_not_found():
    with pytest.raises(EnvParseError, match="File not found"):
        parse_env_file("/nonexistent/.env")


def test_invalid_syntax_no_equals(tmp_path):
    p = write_env(tmp_path, "BADLINE\n")
    with pytest.raises(EnvParseError, match="missing '='"):
        parse_env_file(p)


def test_empty_key(tmp_path):
    p = write_env(tmp_path, "=value\n")
    with pytest.raises(EnvParseError, match="Empty key"):
        parse_env_file(p)


def test_value_with_equals(tmp_path):
    p = write_env(tmp_path, "URL=http://example.com?a=1\n")
    result = parse_env_file(p)
    assert result["URL"] == "http://example.com?a=1"
