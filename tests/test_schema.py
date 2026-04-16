"""Tests for envdiff.schema."""
from pathlib import Path

import pytest

from envdiff.schema import (
    SchemaParseError,
    SchemaResult,
    load_schema,
    validate_against_schema,
)


def write_schema(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env.schema"
    p.write_text(content)
    return p


def test_load_basic(tmp_path):
    p = write_schema(tmp_path, "DB_HOST\nDB_PORT\nSECRET_KEY\n")
    keys = load_schema(p)
    assert keys == {"DB_HOST", "DB_PORT", "SECRET_KEY"}


def test_load_ignores_comments_and_blanks(tmp_path):
    p = write_schema(tmp_path, "# comment\n\nDB_HOST\n")
    assert load_schema(p) == {"DB_HOST"}


def test_load_missing_file(tmp_path):
    with pytest.raises(SchemaParseError, match="not found"):
        load_schema(tmp_path / "missing.schema")


def test_validate_no_violations():
    result = validate_against_schema({"A", "B"}, {"A", "B"})
    assert not result.has_violations
    assert result.extra_keys == []
    assert result.missing_keys == []


def test_validate_missing_keys():
    result = validate_against_schema({"A"}, {"A", "B", "C"})
    assert result.has_violations
    assert result.missing_keys == ["B", "C"]
    assert result.extra_keys == []


def test_validate_extra_keys():
    result = validate_against_schema({"A", "B", "EXTRA"}, {"A", "B"})
    assert result.has_violations
    assert result.extra_keys == ["EXTRA"]
    assert result.missing_keys == []


def test_validate_both():
    result = validate_against_schema({"A", "EXTRA"}, {"A", "REQUIRED"})
    assert result.missing_keys == ["REQUIRED"]
    assert result.extra_keys == ["EXTRA"]


def test_schema_result_sorted(tmp_path):
    result = validate_against_schema(set(), {"Z", "A", "M"})
    assert result.missing_keys == ["A", "M", "Z"]
