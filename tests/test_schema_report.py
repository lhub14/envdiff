"""Tests for schema_report module."""
import json
import pytest

from envdiff.schema import SchemaResult
from envdiff.schema_report import (
    build_schema_report,
    schema_report_to_json,
    schema_report_to_markdown,
)


def make_result(missing=None, invalid=None):
    return SchemaResult(missing_required=missing or [], invalid_pattern=invalid or [])


def test_build_report_no_violations():
    result = make_result()
    report = build_schema_report("a.env", "schema.env", result)
    assert report.total_violations == 0
    assert report.missing_required == []
    assert report.invalid_pattern == []


def test_build_report_counts_violations():
    result = make_result(missing=["A", "B"], invalid=["C"])
    report = build_schema_report("a.env", "schema.env", result)
    assert report.total_violations == 3


def test_json_report_structure():
    result = make_result(missing=["KEY"])
    report = build_schema_report("a.env", "s.env", result)
    data = json.loads(schema_report_to_json(report))
    assert data["missing_required"] == ["KEY"]
    assert data["total_violations"] == 1
    assert "env_file" in data


def test_markdown_report_headings():
    result = make_result(missing=["DB_URL"], invalid=["PORT"])
    report = build_schema_report("a.env", "s.env", result)
    md = schema_report_to_markdown(report)
    assert "## Missing Required Keys" in md
    assert "## Invalid Pattern Keys" in md
    assert "`DB_URL`" in md


def test_markdown_no_violations_message():
    result = make_result()
    report = build_schema_report("a.env", "s.env", result)
    md = schema_report_to_markdown(report)
    assert "No violations" in md
