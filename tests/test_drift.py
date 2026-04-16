"""Tests for envdiff.drift and envdiff.drift_formatter."""
import pytest

from envdiff.baseline import Baseline
from envdiff.drift import DriftResult, detect_drift
from envdiff.drift_formatter import format_drift


def _baseline(snapshots: dict) -> Baseline:
    return Baseline(snapshots=snapshots)


# --- detect_drift ---

def test_no_drift():
    bl = _baseline({"prod": {"A": "1", "B": "2"}})
    result = detect_drift({"A": "1", "B": "2"}, bl, "prod")
    assert not result.has_drift
    assert result.added == []
    assert result.removed == []
    assert result.changed == []


def test_added_key():
    bl = _baseline({"prod": {"A": "1"}})
    result = detect_drift({"A": "1", "B": "2"}, bl, "prod")
    assert result.added == ["B"]
    assert result.has_drift


def test_removed_key():
    bl = _baseline({"prod": {"A": "1", "B": "2"}})
    result = detect_drift({"A": "1"}, bl, "prod")
    assert result.removed == ["B"]
    assert result.has_drift


def test_changed_value():
    bl = _baseline({"prod": {"A": "old"}})
    result = detect_drift({"A": "new"}, bl, "prod")
    assert result.changed == ["A"]
    assert result.has_drift


def test_check_values_disabled():
    bl = _baseline({"prod": {"A": "old"}})
    result = detect_drift({"A": "new"}, bl, "prod", check_values=False)
    assert result.changed == []
    assert not result.has_drift


def test_missing_label_raises():
    bl = _baseline({})
    with pytest.raises(KeyError, match="prod"):
        detect_drift({}, bl, "prod")


# --- format_drift ---

def test_format_no_drift():
    r = DriftResult(label="prod")
    out = format_drift(r, color=False)
    assert "No drift detected" in out
    assert "prod" in out


def test_format_shows_sections():
    r = DriftResult(label="staging", added=["NEW"], removed=["OLD"], changed=["MOD"])
    out = format_drift(r, color=False)
    assert "+ NEW" in out
    assert "- OLD" in out
    assert "~ MOD" in out
