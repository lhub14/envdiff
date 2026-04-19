"""Tests for envdiff.env_interpolate."""
from __future__ import annotations

import pytest
from envdiff.env_interpolate import interpolate_env, has_issues, InterpolateResult


def test_no_references_unchanged():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = interpolate_env(env)
    assert result.resolved == {"FOO": "bar", "BAZ": "qux"}
    assert not has_issues(result)


def test_simple_reference_resolved():
    env = {"HOST": "localhost", "URL": "http://${HOST}/api"}
    result = interpolate_env(env)
    assert result.resolved["URL"] == "http://localhost/api"
    assert not result.unresolved_keys


def test_dollar_without_braces_resolved():
    env = {"PORT": "8080", "ADDR": "0.0.0.0:$PORT"}
    result = interpolate_env(env)
    assert result.resolved["ADDR"] == "0.0.0.0:8080"


def test_chained_references_resolved():
    env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    result = interpolate_env(env)
    assert result.resolved["C"] == "hello_world!"


def test_missing_reference_reported():
    env = {"URL": "http://${MISSING_HOST}/path"}
    result = interpolate_env(env)
    assert "URL" in result.unresolved_keys
    assert has_issues(result)


def test_cycle_detected():
    env = {"A": "${B}", "B": "${A}"}
    result = interpolate_env(env)
    assert set(result.cycles) == {"A", "B"}
    assert has_issues(result)


def test_cycle_value_kept_as_raw():
    env = {"X": "${X}"}
    result = interpolate_env(env)
    assert result.resolved["X"] == "${X}"


def test_has_issues_false_on_clean():
    r = InterpolateResult(resolved={"K": "v"})
    assert not has_issues(r)


def test_has_issues_true_on_unresolved():
    r = InterpolateResult(resolved={}, unresolved_keys=["MISSING"])
    assert has_issues(r)


def test_mixed_resolved_and_unresolved():
    env = {"BASE": "prod", "DB": "${BASE}_db", "GHOST": "${NOPE}"}
    result = interpolate_env(env)
    assert result.resolved["DB"] == "prod_db"
    assert "GHOST" in result.unresolved_keys
