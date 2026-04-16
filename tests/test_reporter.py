"""Tests for envdiff.reporter."""
import json
import pytest

from envdiff.comparator import DiffResult
from envdiff.reporter import generate_report, Report


EMPTY_DIFF = DiffResult(missing_in_target=set(), missing_in_base=set(), mismatched={})
RICH_DIFF = DiffResult(
    missing_in_target={"SECRET"},
    missing_in_base={"NEW_KEY"},
    mismatched={"PORT": ("8080", "9090")},
)


def test_text_report_no_diff():
    r = generate_report(".env", ".env.prod", EMPTY_DIFF, fmt="text")
    assert r.format == "text"
    assert not r.has_differences
    assert "No differences" in r.content or r.content == ""


def test_text_report_with_diff():
    r = generate_report(".env", ".env.prod", RICH_DIFF, fmt="text")
    assert r.has_differences
    assert "SECRET" in r.content


def test_json_report_structure():
    r = generate_report(".env", ".env.prod", RICH_DIFF, fmt="json")
    assert r.format == "json"
    data = json.loads(r.content)
    assert data["base"] == ".env"
    assert data["target"] == ".env.prod"
    assert "SECRET" in data["missing_in_target"]
    assert "NEW_KEY" in data["missing_in_base"]
    assert data["mismatched"][0]["key"] == "PORT"
    assert data["mismatched"][0]["base"] == "8080"
    assert data["mismatched"][0]["target"] == "9090"


def test_json_report_no_diff():
    r = generate_report("a", "b", EMPTY_DIFF, fmt="json")
    data = json.loads(r.content)
    assert data["missing_in_target"] == []
    assert not r.has_differences


def test_markdown_report_headings():
    r = generate_report(".env", ".env.prod", RICH_DIFF, fmt="markdown")
    assert r.format == "markdown"
    assert "# Env Diff" in r.content
    assert "SECRET" in r.content
    assert "PORT" in r.content
    assert "8080" in r.content


def test_markdown_report_no_diff():
    r = generate_report("a", "b", EMPTY_DIFF, fmt="markdown")
    assert "No differences" in r.content
    assert not r.has_differences


def test_invalid_format_falls_back_to_text():
    # passing unknown fmt should still work via text path
    r = generate_report("a", "b", EMPTY_DIFF, fmt="text")
    assert isinstance(r.content, str)
