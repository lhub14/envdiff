"""Tests for envdiff.diff_history."""
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List

import pytest

from envdiff.diff_history import (
    HistoryError,
    HistoryEntry,
    append_entry,
    build_entry,
    clear_history,
    last_entry,
    load_history,
)


@dataclass
class _FakeDiff:
    missing_in_target: List[str]
    missing_in_base: List[str]
    mismatched: Dict[str, object]


def _entry(tmp_path) -> HistoryEntry:
    diff = _FakeDiff(
        missing_in_target=["KEY_A"],
        missing_in_base=[],
        mismatched={"KEY_B": ("x", "y")},
    )
    return build_entry(str(tmp_path / "base.env"), str(tmp_path / "prod.env"), diff)


def test_build_entry_captures_fields(tmp_path):
    e = _entry(tmp_path)
    assert "KEY_A" in e.missing_in_target
    assert "KEY_B" in e.mismatched
    assert e.had_diff is True


def test_build_entry_no_diff(tmp_path):
    diff = _FakeDiff([], [], {})
    e = build_entry("a", "b", diff)
    assert e.had_diff is False


def test_append_and_load(tmp_path):
    store = tmp_path / "hist.json"
    e = _entry(tmp_path)
    append_entry(e, store)
    append_entry(e, store)
    loaded = load_history(store)
    assert len(loaded) == 2
    assert loaded[0].missing_in_target == ["KEY_A"]


def test_load_missing_file_returns_empty(tmp_path):
    store = tmp_path / "missing.json"
    assert load_history(store) == []


def test_load_corrupt_file_raises(tmp_path):
    store = tmp_path / "bad.json"
    store.write_text("not json")
    with pytest.raises(HistoryError):
        load_history(store)


def test_last_entry(tmp_path):
    store = tmp_path / "hist.json"
    e1 = build_entry("a", "b", _FakeDiff(["X"], [], {}))
    e2 = build_entry("a", "b", _FakeDiff(["Y"], [], {}))
    append_entry(e1, store)
    append_entry(e2, store)
    last = last_entry(store)
    assert last.missing_in_target == ["Y"]


def test_last_entry_empty_store(tmp_path):
    store = tmp_path / "empty.json"
    assert last_entry(store) is None


def test_clear_history(tmp_path):
    store = tmp_path / "hist.json"
    e = _entry(tmp_path)
    append_entry(e, store)
    count = clear_history(store)
    assert count == 1
    assert not store.exists()


def test_clear_missing_store_returns_zero(tmp_path):
    store = tmp_path / "none.json"
    assert clear_history(store) == 0
