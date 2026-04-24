"""Tests for envdiff.env_mask."""
from __future__ import annotations

import pytest

from envdiff.env_mask import MaskResult, has_masked, mask_env, _mask_value


# ---------------------------------------------------------------------------
# _mask_value unit tests
# ---------------------------------------------------------------------------

def test_mask_value_full_replacement():
    assert _mask_value("secret123", "***", 0) == "***"


def test_mask_value_reveal_chars():
    assert _mask_value("secret123", "***", 3) == "***123"


def test_mask_value_reveal_chars_exceeds_length_returns_mask():
    assert _mask_value("ab", "***", 10) == "***"


def test_mask_value_empty_string_unchanged():
    assert _mask_value("", "***", 0) == ""


# ---------------------------------------------------------------------------
# mask_env tests
# ---------------------------------------------------------------------------

def test_non_sensitive_keys_unchanged():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    result = mask_env(env)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["PORT"] == "8080"
    assert result.masked_keys == []


def test_sensitive_key_is_masked():
    env = {"API_KEY": "supersecret", "HOST": "localhost"}
    result = mask_env(env)
    assert result.masked["API_KEY"] == "***"
    assert result.masked["HOST"] == "localhost"
    assert "API_KEY" in result.masked_keys


def test_password_key_masked():
    env = {"DB_PASSWORD": "hunter2"}
    result = mask_env(env)
    assert result.masked["DB_PASSWORD"] == "***"


def test_extra_keys_are_masked():
    env = {"MY_CUSTOM": "value", "OTHER": "plain"}
    result = mask_env(env, extra_keys=["MY_CUSTOM"])
    assert result.masked["MY_CUSTOM"] == "***"
    assert result.masked["OTHER"] == "plain"


def test_extra_keys_case_insensitive():
    env = {"MY_TOKEN": "abc"}
    result = mask_env(env, extra_keys=["my_token"])
    assert result.masked["MY_TOKEN"] == "***"


def test_original_dict_not_mutated():
    env = {"SECRET_KEY": "shh"}
    original_copy = dict(env)
    mask_env(env)
    assert env == original_copy


def test_has_masked_true_when_keys_masked():
    env = {"TOKEN": "abc"}
    result = mask_env(env)
    assert has_masked(result)


def test_has_masked_false_when_no_sensitive_keys():
    env = {"APP_NAME": "demo"}
    result = mask_env(env)
    assert not has_masked(result)


def test_reveal_chars_propagated():
    env = {"SECRET": "abcdef"}
    result = mask_env(env, reveal_chars=2)
    assert result.masked["SECRET"] == "***ef"


def test_custom_mask_string():
    env = {"API_SECRET": "xyz"}
    result = mask_env(env, mask="[REDACTED]")
    assert result.masked["API_SECRET"] == "[REDACTED]"
