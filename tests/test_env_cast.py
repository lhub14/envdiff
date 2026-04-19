"""Tests for envdiff.env_cast."""
from __future__ import annotations

import pytest
from envdiff.env_cast import cast_env, cast_value, has_issues, CastResult


def _env(**kwargs: str) -> dict[str, str]:
    return dict(kwargs)


def test_no_schema_returns_strings():
    result = cast_env(_env(PORT="8080", HOST="localhost"), {})
    assert result.values["PORT"] == "8080"
    assert result.values["HOST"] == "localhost"
    assert not has_issues(result)


def test_int_cast_success():
    result = cast_env(_env(PORT="8080"), {"PORT": "int"})
    assert result.values["PORT"] == 8080
    assert isinstance(result.values["PORT"], int)
    assert not has_issues(result)


def test_float_cast_success():
    result = cast_env(_env(RATIO="0.75"), {"RATIO": "float"})
    assert result.values["RATIO"] == pytest.approx(0.75)
    assert not has_issues(result)


@pytest.mark.parametrize("raw,expected", [
    ("true", True), ("1", True), ("yes", True), ("on", True),
    ("false", False), ("0", False), ("no", False),
])
def test_bool_cast(raw: str, expected: bool):
    result = cast_env({"FLAG": raw}, {"FLAG": "bool"})
    assert result.values["FLAG"] is expected


def test_int_cast_failure_keeps_raw():
    result = cast_env(_env(PORT="not_a_number"), {"PORT": "int"})
    assert has_issues(result)
    assert len(result.issues) == 1
    assert result.issues[0].key == "PORT"
    assert result.issues[0].target_type == "int"
    assert result.values["PORT"] == "not_a_number"  # raw preserved


def test_unknown_type_treated_as_str():
    result = cast_env(_env(X="hello"), {"X": "uuid"})
    assert result.values["X"] == "hello"
    assert not has_issues(result)


def test_cast_value_helper_success():
    assert cast_value("42", "int") == 42


def test_cast_value_helper_failure_returns_none():
    assert cast_value("abc", "float") is None


def test_empty_env_returns_empty_result():
    result = cast_env({}, {"PORT": "int"})
    assert result.values == {}
    assert not has_issues(result)


def test_multiple_issues_reported():
    env = {"A": "bad", "B": "also_bad", "C": "3"}
    schema = {"A": "int", "B": "float", "C": "int"}
    result = cast_env(env, schema)
    assert len(result.issues) == 2
    assert result.values["C"] == 3
