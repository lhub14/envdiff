"""Tests for envdiff.pin."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.pin import (
    PinError,
    diff_against_pin,
    is_clean,
    load_pin,
    save_pin,
)


def test_save_and_load(tmp_path: Path) -> None:
    pin = tmp_path / "pins" / "base.json"
    save_pin(["FOO", "BAR", "BAZ"], pin)
    keys = load_pin(pin)
    assert keys == ["BAR", "BAZ", "FOO"]


def test_save_deduplicates(tmp_path: Path) -> None:
    pin = tmp_path / "pin.json"
    save_pin(["A", "A", "B"], pin)
    assert load_pin(pin) == ["A", "B"]


def test_load_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(PinError, match="not found"):
        load_pin(tmp_path / "ghost.json")


def test_load_invalid_json_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("not json")
    with pytest.raises(PinError, match="Invalid pin file"):
        load_pin(bad)


def test_load_missing_keys_field_raises(tmp_path: Path) -> None:
    f = tmp_path / "pin.json"
    f.write_text(json.dumps({"version": 1}))
    with pytest.raises(PinError, match="missing 'keys'"):
        load_pin(f)


def test_diff_added_and_removed(tmp_path: Path) -> None:
    pin = tmp_path / "pin.json"
    save_pin(["FOO", "BAR"], pin)
    result = diff_against_pin({"FOO": "1", "NEW": "2"}, pin)
    assert result["added"] == ["NEW"]
    assert result["removed"] == ["BAR"]


def test_diff_no_changes(tmp_path: Path) -> None:
    pin = tmp_path / "pin.json"
    save_pin(["A", "B"], pin)
    result = diff_against_pin({"A": "1", "B": "2"}, pin)
    assert result == {"added": [], "removed": []}


def test_is_clean_true(tmp_path: Path) -> None:
    pin = tmp_path / "pin.json"
    save_pin(["X"], pin)
    assert is_clean({"X": "val"}, pin) is True


def test_is_clean_false(tmp_path: Path) -> None:
    pin = tmp_path / "pin.json"
    save_pin(["X", "Y"], pin)
    assert is_clean({"X": "val"}, pin) is False
