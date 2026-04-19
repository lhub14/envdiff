"""Tests for envdiff.env_dedup."""
import pytest
from envdiff.env_dedup import find_duplicate_values, deduplicate_env, DedupResult


def test_no_duplicates_returns_empty_result():
    env = {"A": "1", "B": "2", "C": "3"}
    result = find_duplicate_values(env)
    assert not result.has_duplicates
    assert result.duplicates == {}


def test_duplicate_value_detected():
    env = {"A": "secret", "B": "other", "C": "secret"}
    result = find_duplicate_values(env)
    assert result.has_duplicates
    assert set(result.duplicates["secret"]) == {"A", "C"}


def test_empty_values_ignored():
    env = {"A": "", "B": "", "C": "real"}
    result = find_duplicate_values(env)
    assert not result.has_duplicates


def test_multiple_duplicate_groups():
    env = {"A": "x", "B": "x", "C": "y", "D": "y"}
    result = find_duplicate_values(env)
    assert len(result.duplicates) == 2


def test_dedup_keep_first():
    env = {"A": "val", "B": "other", "C": "val"}
    cleaned, removed = deduplicate_env(env, keep="first")
    assert "A" in cleaned
    assert "C" not in cleaned
    assert removed == ["C"]


def test_dedup_keep_last():
    env = {"A": "val", "B": "other", "C": "val"}
    cleaned, removed = deduplicate_env(env, keep="last")
    assert "C" in cleaned
    assert "A" not in cleaned
    assert removed == ["A"]


def test_dedup_no_duplicates_unchanged():
    env = {"A": "1", "B": "2"}
    cleaned, removed = deduplicate_env(env)
    assert cleaned == env
    assert removed == []


def test_dedup_invalid_keep_raises():
    with pytest.raises(ValueError, match="keep must be"):
        deduplicate_env({"A": "1"}, keep="middle")


def test_dedup_does_not_mutate_original():
    env = {"A": "dup", "B": "dup"}
    original = dict(env)
    deduplicate_env(env)
    assert env == original
