"""Tests for env_diff_timeline module."""
from __future__ import annotations

import json
import pathlib
import pytest

from envdiff.env_diff_timeline import build_timeline, TimelineResult, TimelineEntry


def _write_store(tmp_path: pathlib.Path, data: dict) -> str:
    store = tmp_path / "snapshots.json"
    store.write_text(json.dumps(data))
    return str(store)


def _snap(env: dict, ts: str = "2024-01-01T00:00:00") -> dict:
    return {"env": env, "timestamp": ts}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def test_no_changes_all_clean(tmp_path):
    store = _write_store(tmp_path, {
        "base": _snap({"A": "1", "B": "2"}, "2024-01-01T00:00:00"),
        "v1":   _snap({"A": "1", "B": "2"}, "2024-01-02T00:00:00"),
    })
    result = build_timeline(store, "base")
    assert isinstance(result, TimelineResult)
    assert len(result.entries) == 1
    assert result.entries[0].is_clean
    assert not result.has_changes


def test_missing_in_target_detected(tmp_path):
    store = _write_store(tmp_path, {
        "base": _snap({"A": "1", "B": "2"}),
        "v1":   _snap({"A": "1"}),
    })
    result = build_timeline(store, "base")
    entry = result.entries[0]
    assert "B" in entry.missing_in_target
    assert entry.total_issues == 1
    assert result.has_changes


def test_missing_in_base_detected(tmp_path):
    store = _write_store(tmp_path, {
        "base": _snap({"A": "1"}),
        "v1":   _snap({"A": "1", "B": "2"}),
    })
    result = build_timeline(store, "base")
    entry = result.entries[0]
    assert "B" in entry.missing_in_base


def test_mismatch_detected(tmp_path):
    store = _write_store(tmp_path, {
        "base": _snap({"A": "1"}),
        "v1":   _snap({"A": "99"}),
    })
    result = build_timeline(store, "base")
    entry = result.entries[0]
    assert "A" in entry.mismatched


def test_ignore_values_skips_mismatch(tmp_path):
    store = _write_store(tmp_path, {
        "base": _snap({"A": "1"}),
        "v1":   _snap({"A": "99"}),
    })
    result = build_timeline(store, "base", ignore_values=True)
    assert result.entries[0].is_clean


def test_target_labels_filter(tmp_path):
    store = _write_store(tmp_path, {
        "base": _snap({"A": "1"}),
        "v1":   _snap({"A": "1"}),
        "v2":   _snap({"A": "bad"}),
    })
    result = build_timeline(store, "base", target_labels=["v1"])
    assert len(result.entries) == 1
    assert result.entries[0].label == "v1"


def test_entries_sorted_by_timestamp(tmp_path):
    store = _write_store(tmp_path, {
        "base": _snap({"A": "1"}, "2024-01-01T00:00:00"),
        "v2":   _snap({"A": "1"}, "2024-03-01T00:00:00"),
        "v1":   _snap({"A": "1"}, "2024-02-01T00:00:00"),
    })
    result = build_timeline(store, "base")
    labels = [e.label for e in result.entries]
    assert labels == ["v1", "v2"]


def test_missing_base_label_raises(tmp_path):
    store = _write_store(tmp_path, {
        "v1": _snap({"A": "1"}),
    })
    with pytest.raises(KeyError, match="base"):
        build_timeline(store, "base")


def test_worst_entry_returns_max_issues(tmp_path):
    store = _write_store(tmp_path, {
        "base": _snap({"A": "1", "B": "2", "C": "3"}),
        "v1":   _snap({"A": "1"}),
        "v2":   _snap({"A": "1", "B": "2"}),
    })
    result = build_timeline(store, "base")
    worst = result.worst_entry
    assert worst is not None
    assert worst.label == "v1"
