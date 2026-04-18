"""Tests for envdiff.env_validate."""
import pytest
from envdiff.env_validate import ValidationIssue, ValidationResult, validate_env


def _env(**kwargs: str):
    return dict(kwargs)


def test_valid_int_passes():
    result = validate_env(_env(PORT="8080"), {"PORT": "int"})
    assert result.valid


def test_invalid_int_fails():
    result = validate_env(_env(PORT="abc"), {"PORT": "int"})
    assert not result.valid
    assert result.issues[0].key == "PORT"
    assert result.issues[0].rule == "int"


def test_valid_bool_passes():
    for val in ("true", "false", "1", "0", "yes", "no", "True", "FALSE"):
        r = validate_env(_env(DEBUG=val), {"DEBUG": "bool"})
        assert r.valid, f"Expected {val!r} to be valid bool"


def test_invalid_bool_fails():
    result = validate_env(_env(DEBUG="maybe"), {"DEBUG": "bool"})
    assert not result.valid


def test_url_rule():
    assert validate_env(_env(URL="https://example.com"), {"URL": "url"}).valid
    assert not validate_env(_env(URL="ftp://bad"), {"URL": "url"}).valid


def test_email_rule():
    assert validate_env(_env(ADMIN="a@b.com"), {"ADMIN": "email"}).valid
    assert not validate_env(_env(ADMIN="notanemail"), {"ADMIN": "email"}).valid


def test_nonempty_rule():
    assert validate_env(_env(NAME="x"), {"NAME": "nonempty"}).valid
    assert not validate_env(_env(NAME=""), {"NAME": "nonempty"}).valid


def test_custom_regex_rule():
    result = validate_env(_env(HEX="#a1b2c3"), {"HEX": r"^#[0-9a-fA-F]{6}$"})
    assert result.valid

    result = validate_env(_env(HEX="red"), {"HEX": r"^#[0-9a-fA-F]{6}$"})
    assert not result.valid


def test_missing_key_not_reported():
    """Keys absent from env are skipped — comparator handles missing keys."""
    result = validate_env({}, {"PORT": "int"})
    assert result.valid
    assert result.issues == []


def test_multiple_issues_collected():
    env = _env(PORT="bad", DEBUG="maybe")
    result = validate_env(env, {"PORT": "int", "DEBUG": "bool"})
    assert len(result.issues) == 2
    keys = {i.key for i in result.issues}
    assert keys == {"PORT", "DEBUG"}


def test_issue_message_contains_key_and_value():
    result = validate_env(_env(PORT="xyz"), {"PORT": "int"})
    assert "PORT" in result.issues[0].message
    assert "xyz" in result.issues[0].message
