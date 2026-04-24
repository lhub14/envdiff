"""Tests for envdiff.env_alias and envdiff.alias_formatter."""
import pytest

from envdiff.env_alias import AliasGroup, AliasResult, detect_aliases, has_aliases
from envdiff.alias_formatter import format_alias_result


# ---------------------------------------------------------------------------
# detect_aliases
# ---------------------------------------------------------------------------

def test_no_aliases_when_all_values_unique():
    envs = {
        "a.env": {"FOO": "hello", "BAR": "world"},
        "b.env": {"BAZ": "other"},
    }
    result = detect_aliases(envs)
    assert not has_aliases(result)
    assert result.checked == 3


def test_alias_detected_across_files():
    envs = {
        "a.env": {"DB_PASS": "supersecret"},
        "b.env": {"DATABASE_PASSWORD": "supersecret"},
    }
    result = detect_aliases(envs)
    assert has_aliases(result)
    assert len(result.groups) == 1
    group = result.groups[0]
    assert group.value == "supersecret"
    keys = {k for _, k in group.keys}
    assert keys == {"DB_PASS", "DATABASE_PASSWORD"}


def test_alias_detected_within_same_file():
    envs = {
        "a.env": {"OLD_KEY": "sharedvalue", "NEW_KEY": "sharedvalue"},
    }
    result = detect_aliases(envs)
    assert has_aliases(result)
    assert result.groups[0].value == "sharedvalue"


def test_short_values_ignored_by_default():
    envs = {
        "a.env": {"A": "ok", "B": "ok"},  # len 2 < default min_length 3
    }
    result = detect_aliases(envs)
    assert not has_aliases(result)


def test_min_length_override():
    envs = {
        "a.env": {"A": "ok", "B": "ok"},
    }
    result = detect_aliases(envs, min_length=2)
    assert has_aliases(result)


def test_empty_envs_returns_empty_result():
    result = detect_aliases({})
    assert not has_aliases(result)
    assert result.checked == 0


def test_multiple_alias_groups():
    envs = {
        "a.env": {"X": "alpha_value", "Y": "beta_value"},
        "b.env": {"X2": "alpha_value", "Y2": "beta_value"},
    }
    result = detect_aliases(envs)
    assert len(result.groups) == 2


# ---------------------------------------------------------------------------
# format_alias_result
# ---------------------------------------------------------------------------

def test_format_no_aliases():
    result = AliasResult(groups=[], checked=5)
    output = format_alias_result(result, no_colour=True)
    assert "No aliases" in output
    assert "5" in output


def test_format_with_aliases():
    result = AliasResult(
        groups=[
            AliasGroup(value="secretvalue", keys=[("prod.env", "DB_PASS"), ("staging.env", "DATABASE_PASSWORD")])
        ],
        checked=10,
    )
    output = format_alias_result(result, no_colour=True)
    assert "1 alias group" in output
    assert "secretvalue" in output
    assert "DB_PASS" in output
    assert "DATABASE_PASSWORD" in output


def test_format_long_value_truncated():
    long_val = "x" * 80
    result = AliasResult(
        groups=[AliasGroup(value=long_val, keys=[("a.env", "K1"), ("b.env", "K2")])],
        checked=2,
    )
    output = format_alias_result(result, no_colour=True)
    assert "\u2026" in output  # ellipsis character
