"""Tests for envdiff.diff_filter."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.diff_filter import FilterOptions, filter_diff


def _result() -> DiffResult:
    return DiffResult(
        missing_in_target=["DB_HOST", "DB_PORT", "SECRET_KEY"],
        missing_in_base=["LEGACY_FLAG"],
        mismatched={"APP_ENV": ("production", "staging"), "LOG_LEVEL": ("info", "debug")},
    )


def test_no_filter_returns_all():
    r = filter_diff(_result(), FilterOptions())
    assert r.missing_in_target == ["DB_HOST", "DB_PORT", "SECRET_KEY"]
    assert r.missing_in_base == ["LEGACY_FLAG"]
    assert set(r.mismatched) == {"APP_ENV", "LOG_LEVEL"}


def test_include_pattern_filters_keys():
    opts = FilterOptions(include_patterns=["DB_*"])
    r = filter_diff(_result(), opts)
    assert r.missing_in_target == ["DB_HOST", "DB_PORT"]
    assert r.missing_in_base == []
    assert r.mismatched == {}


def test_exclude_pattern_removes_keys():
    opts = FilterOptions(exclude_patterns=["DB_*", "LOG_*"])
    r = filter_diff(_result(), opts)
    assert "DB_HOST" not in r.missing_in_target
    assert "DB_PORT" not in r.missing_in_target
    assert "SECRET_KEY" in r.missing_in_target
    assert "LOG_LEVEL" not in r.mismatched
    assert "APP_ENV" in r.mismatched


def test_only_missing_flag():
    opts = FilterOptions(only_missing=True)
    r = filter_diff(_result(), opts)
    assert r.missing_in_target == ["DB_HOST", "DB_PORT", "SECRET_KEY"]
    assert r.missing_in_base == []
    assert r.mismatched == {}


def test_only_extra_flag():
    opts = FilterOptions(only_extra=True)
    r = filter_diff(_result(), opts)
    assert r.missing_in_target == []
    assert r.missing_in_base == ["LEGACY_FLAG"]
    assert r.mismatched == {}


def test_only_mismatch_flag():
    opts = FilterOptions(only_mismatch=True)
    r = filter_diff(_result(), opts)
    assert r.missing_in_target == []
    assert r.missing_in_base == []
    assert set(r.mismatched) == {"APP_ENV", "LOG_LEVEL"}


def test_include_and_only_mismatch_combined():
    opts = FilterOptions(include_patterns=["APP_*"], only_mismatch=True)
    r = filter_diff(_result(), opts)
    assert r.mismatched == {"APP_ENV": ("production", "staging")}


def test_does_not_mutate_original():
    original = _result()
    filter_diff(original, FilterOptions(include_patterns=["NOPE"]))
    assert len(original.missing_in_target) == 3
