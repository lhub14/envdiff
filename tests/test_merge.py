"""Tests for envdiff.merge."""
import pytest
from envdiff.merge import merge_envs, has_conflicts, MergeResult


A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
B = {"HOST": "remotehost", "PORT": "5432", "EXTRA": "yes"}
C = {"HOST": "thirdhost", "NEW": "val"}


def test_no_conflicts_single_source():
    result = merge_envs({"a": A})
    assert result.merged == A
    assert not has_conflicts(result)


def test_merge_disjoint_keys():
    result = merge_envs({"a": {"X": "1"}, "b": {"Y": "2"}})
    assert result.merged == {"X": "1", "Y": "2"}
    assert not has_conflicts(result)


def test_conflict_detected_on_different_values():
    result = merge_envs({"a": A, "b": B})
    assert has_conflicts(result)
    assert "HOST" in result.conflicts
    assert "PORT" not in result.conflicts  # same value


def test_strategy_first_keeps_first_value():
    result = merge_envs({"a": A, "b": B}, strategy="first")
    assert result.merged["HOST"] == "localhost"


def test_strategy_last_keeps_last_value():
    result = merge_envs({"a": A, "b": B}, strategy="last")
    assert result.merged["HOST"] == "remotehost"


def test_conflict_entries_contain_all_sources():
    result = merge_envs({"a": A, "b": B, "c": C})
    entries = result.conflicts["HOST"]
    sources = [e[0] for e in entries]
    assert "a" in sources
    assert "b" in sources
    assert "c" in sources


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown merge strategy"):
        merge_envs({"a": A}, strategy="random")


def test_empty_sources():
    result = merge_envs({})
    assert result.merged == {}
    assert not has_conflicts(result)


def test_all_same_values_no_conflict():
    result = merge_envs({"a": {"K": "v"}, "b": {"K": "v"}, "c": {"K": "v"}})
    assert not has_conflicts(result)
    assert result.merged["K"] == "v"
