"""Tests for schema_formatter module."""
import pytest

from envdiff.schema import SchemaResult
from envdiff.schema_formatter import format_schema_result


def test_format_no_violations():
    result = SchemaResult(missing_required=[], invalid_pattern=[])
    output = format_schema_result(result)
    assert "no violations" in output.lower() or output.strip() != ""


def test_format_shows_missing_keys():
    result = SchemaResult(missing_required=["API_KEY", "SECRET"], invalid_pattern=[])
    output = format_schema_result(result)
    assert "API_KEY" in output
    assert "SECRET" in output


def test_format_shows_invalid_pattern_keys():
    result = SchemaResult(missing_required=[], invalid_pattern=["PORT"])
    output = format_schema_result(result)
    assert "PORT" in output


def test_format_combined_violations():
    result = SchemaResult(missing_required=["A"], invalid_pattern=["B"])
    output = format_schema_result(result)
    assert "A" in output
    assert "B" in output
