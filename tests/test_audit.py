"""Tests for envdiff.audit module."""
import json
from pathlib import Path

import pytest

from envdiff.audit import AuditEntry, append_to_log, build_entry, load_log
from envdiff.comparator import DiffResult


def _result(missing_target=(), missing_base=(), mismatched=()):
    return DiffResult(
        missing_in_target=set(missing_target),
        missing_in_base=set(missing_base),
        mismatched=set(mismatched),
    )


def test_build_entry_no_diff():
    r = _result()
    e = build_entry(".env", ".env.prod", r)
    assert e.has_diff is False
    assert e.missing_in_target == []
    assert e.base == ".env"


def test_build_entry_with_diff():
    r = _result(missing_target=["SECRET"], mismatched=["PORT"])
    e = build_entry(".env", ".env.prod", r)
    assert e.has_diff is True
    assert "SECRET" in e.missing_in_target
    assert "PORT" in e.mismatched


def test_append_and_load(tmp_path):
    log = tmp_path / "audit.log"
    r = _result(missing_target=["KEY"])
    e = build_entry("a", "b", r)
    append_to_log(e, log)
    append_to_log(e, log)
    entries = load_log(log)
    assert len(entries) == 2
    assert entries[0].missing_in_target == ["KEY"]


def test_load_missing_file(tmp_path):
    entries = load_log(tmp_path / "nonexistent.log")
    assert entries == []


def test_append_creates_parents(tmp_path):
    log = tmp_path / "sub" / "dir" / "audit.log"
    e = build_entry("x", "y", _result())
    append_to_log(e, log)
    assert log.exists()


def test_log_is_valid_jsonl(tmp_path):
    log = tmp_path / "audit.log"
    e = build_entry("a", "b", _result(mismatched=["Z"]))
    append_to_log(e, log)
    line = log.read_text().strip()
    data = json.loads(line)
    assert "timestamp" in data
    assert data["mismatched"] == ["Z"]
