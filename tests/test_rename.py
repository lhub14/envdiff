"""Tests for envdiff.rename."""
from __future__ import annotations

import pytest
from envdiff.rename import detect_renames, has_candidates, RenameResult


def test_no_candidates_identical_keys():
    base = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = detect_renames(base, base.copy())
    assert result.candidates == []
    assert result.unmatched_base == []
    assert result.unmatched_target == []


def test_obvious_rename_detected():
    base = {"DATABASE_URL": "x"}
    target = {"DATABASE_URI": "x"}
    result = detect_renames(base, target)
    assert len(result.candidates) == 1
    c = result.candidates[0]
    assert c.old_key == "DATABASE_URL"
    assert c.new_key == "DATABASE_URI"
    assert c.score > 0.6


def test_unmatched_keys_reported():
    base = {"FOO": "1", "TOTALLY_DIFFERENT": "2"}
    target = {"BAR": "1", "ZZZZZZZZZZZ": "2"}
    result = detect_renames(base, target, threshold=0.9)
    # Nothing should match at 90% threshold
    assert result.candidates == []
    assert "FOO" in result.unmatched_base or "TOTALLY_DIFFERENT" in result.unmatched_base


def test_threshold_filters_low_scores():
    base = {"ABC": "1"}
    target = {"XYZ": "1"}
    result = detect_renames(base, target, threshold=0.99)
    assert result.candidates == []
    assert result.unmatched_base == ["ABC"]
    assert result.unmatched_target == ["XYZ"]


def test_has_candidates_true_false():
    base = {"API_KEY": "a"}
    target = {"API_KEYS": "a"}
    result = detect_renames(base, target)
    assert has_candidates(result) is True

    empty = RenameResult()
    assert has_candidates(empty) is False


def test_common_keys_excluded_from_unmatched():
    base = {"SHARED": "1", "OLD_NAME": "2"}
    target = {"SHARED": "1", "NEW_NAME": "2"}
    result = detect_renames(base, target)
    assert "SHARED" not in result.unmatched_base
    assert "SHARED" not in result.unmatched_target
