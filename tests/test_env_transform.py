"""Tests for envdiff.env_transform"""
import pytest
from envdiff.env_transform import (
    TransformRule, transform_env, has_changes, _matches,
)


def _rule(pattern: str, op: str, arg: str | None = None) -> TransformRule:
    return TransformRule(key_pattern=pattern, operation=op, argument=arg)


def test_no_rules_returns_unchanged():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = transform_env(env, [])
    assert result.transformed == env
    assert not has_changes(result)


def test_uppercase_operation():
    env = {"HOST": "localhost"}
    result = transform_env(env, [_rule("HOST", "uppercase")])
    assert result.transformed["HOST"] == "LOCALHOST"
    assert has_changes(result)


def test_lowercase_operation():
    env = {"ENV": "PRODUCTION"}
    result = transform_env(env, [_rule("ENV", "lowercase")])
    assert result.transformed["ENV"] == "production"


def test_strip_operation():
    env = {"KEY": "  value  "}
    result = transform_env(env, [_rule("KEY", "strip")])
    assert result.transformed["KEY"] == "value"


def test_prefix_operation():
    env = {"DB_URL": "mydb"}
    result = transform_env(env, [_rule("DB_URL", "prefix", "postgres://")])
    assert result.transformed["DB_URL"] == "postgres://mydb"


def test_suffix_operation():
    env = {"APP_NAME": "myapp"}
    result = transform_env(env, [_rule("APP_NAME", "suffix", "_v2")])
    assert result.transformed["APP_NAME"] == "myapp_v2"


def test_replace_operation():
    env = {"URL": "http://example.com"}
    result = transform_env(env, [_rule("URL", "replace", "http:https")])
    assert result.transformed["URL"] == "https://example.com"


def test_wildcard_suffix_pattern():
    env = {"DB_URL": "db", "API_URL": "api", "NAME": "app"}
    result = transform_env(env, [_rule("*_URL", "uppercase")])
    assert result.transformed["DB_URL"] == "DB"
    assert result.transformed["API_URL"] == "API"
    assert result.transformed["NAME"] == "app"


def test_wildcard_prefix_pattern():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "OTHER": "x"}
    result = transform_env(env, [_rule("DB_*", "uppercase")])
    assert result.transformed["DB_HOST"] == "LOCALHOST"
    assert result.transformed["DB_PORT"] == "5432"  # already upper-ish; value unchanged
    assert result.transformed["OTHER"] == "x"


def test_no_change_not_recorded():
    env = {"KEY": "VALUE"}
    result = transform_env(env, [_rule("KEY", "uppercase")])
    assert not has_changes(result)  # already uppercase


def test_changes_list_has_correct_format():
    env = {"FOO": "bar"}
    result = transform_env(env, [_rule("FOO", "uppercase")])
    assert len(result.changes) == 1
    assert "FOO" in result.changes[0]
    assert "bar" in result.changes[0]
    assert "BAR" in result.changes[0]


def test_matches_star_matches_all():
    assert _matches("ANYTHING", "*")


def test_matches_exact():
    assert _matches("FOO", "FOO")
    assert not _matches("BAR", "FOO")
