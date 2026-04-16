"""Tests for envdiff.redact."""

import pytest
from envdiff.redact import is_sensitive, redact_env, redact_value, REDACTED


@pytest.mark.parametrize("key", [
    "PASSWORD",
    "db_password",
    "API_KEY",
    "auth_token",
    "SECRET",
    "AWS_SECRET",
    "PRIVATE_KEY",
    "access_key_id",
    "MY_CREDENTIAL",
])
def test_is_sensitive_true(key):
    assert is_sensitive(key) is True


@pytest.mark.parametrize("key", [
    "HOST",
    "PORT",
    "DEBUG",
    "LOG_LEVEL",
    "DATABASE_URL",
])
def test_is_sensitive_false(key):
    assert is_sensitive(key) is False


def test_redact_env_replaces_sensitive():
    env = {"HOST": "localhost", "API_KEY": "abc123", "PORT": "5432"}
    result = redact_env(env)
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"
    assert result["API_KEY"] == REDACTED


def test_redact_env_extra_keys():
    env = {"HOST": "localhost", "MY_CUSTOM": "sensitive"}
    result = redact_env(env, extra_keys=frozenset({"MY_CUSTOM"}))
    assert result["HOST"] == "localhost"
    assert result["MY_CUSTOM"] == REDACTED


def test_redact_env_does_not_mutate_original():
    env = {"API_KEY": "secret"}
    redact_env(env)
    assert env["API_KEY"] == "secret"


def test_redact_value_sensitive():
    assert redact_value("PASSWORD", "hunter2") == REDACTED


def test_redact_value_not_sensitive():
    assert redact_value("HOST", "localhost") == "localhost"


def test_redact_value_extra_keys():
    assert redact_value("CUSTOM", "val", extra_keys=frozenset({"CUSTOM"})) == REDACTED


def test_redact_env_empty():
    assert redact_env({}) == {}
