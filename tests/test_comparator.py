"""Tests for envdiff.comparator."""

import pytest

from envdiff.comparator import DiffResult, compare_envs


def test_no_differences():
    env = {"A": "1", "B": "2"}
    result = compare_envs(env, env.copy(), base_name="a", target_name="b")
    assert not result.has_differences
    assert result.missing_in_target == []
    assert result.missing_in_base == []
    assert result.value_mismatches == {}


def test_missing_in_target():
    base = {"A": "1", "B": "2"}
    target = {"A": "1"}
    result = compare_envs(base, target)
    assert result.missing_in_target == ["B"]
    assert result.missing_in_base == []


def test_missing_in_base():
    base = {"A": "1"}
    target = {"A": "1", "C": "3"}
    result = compare_envs(base, target)
    assert result.missing_in_base == ["C"]
    assert result.missing_in_target == []


def test_value_mismatch():
    base = {"A": "1", "B": "old"}
    target = {"A": "1", "B": "new"}
    result = compare_envs(base, target)
    assert "B" in result.value_mismatches
    assert result.value_mismatches["B"] == ("old", "new")


def test_value_mismatch_skipped_when_disabled():
    base = {"A": "1", "B": "old"}
    target = {"A": "1", "B": "new"}
    result = compare_envs(base, target, check_values=False)
    assert result.value_mismatches == {}


def test_none_values_differ():
    base = {"A": None}
    target = {"A": ""}
    result = compare_envs(base, target)
    assert "A" in result.value_mismatches


def test_sorted_keys():
    base = {"Z": "1", "A": "2", "M": "3"}
    target = {}
    result = compare_envs(base, target)
    assert result.missing_in_target == ["A", "M", "Z"]


def test_has_differences_flag():
    result = DiffResult(base_name="a", target_name="b")
    assert not result.has_differences
    result.missing_in_target.append("X")
    assert result.has_differences
