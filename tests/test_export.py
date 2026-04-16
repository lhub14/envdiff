"""Unit tests for envdiff.export."""
import json
import pytest
from envdiff.export import export_env, ExportError, SUPPORTED_FORMATS


ENV = {"DB_HOST": "localhost", "SECRET_KEY": "abc 123", "PORT": "5432"}


def test_json_format_is_valid_json():
    result = export_env(ENV, "json")
    parsed = json.loads(result)
    assert parsed["PORT"] == "5432"
    assert parsed["DB_HOST"] == "localhost"


def test_json_keys_sorted():
    result = export_env(ENV, "json")
    parsed = json.loads(result)
    assert list(parsed.keys()) == sorted(parsed.keys())


def test_dotenv_format_basic():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = export_env(env, "dotenv")
    assert "FOO=bar" in result
    assert "BAZ=qux" in result


def test_dotenv_quotes_values_with_spaces():
    env = {"MSG": "hello world"}
    result = export_env(env, "dotenv")
    assert 'MSG="hello world"' in result


def test_dotenv_quotes_values_with_hash():
    env = {"VAL": "foo#bar"}
    result = export_env(env, "dotenv")
    assert '"' in result


def test_shell_format_uses_export():
    env = {"HOME": "/root"}
    result = export_env(env, "shell")
    assert "export HOME='/root'" in result


def test_shell_escapes_single_quotes():
    env = {"VAL": "it's"}
    result = export_env(env, "shell")
    assert "VAL=" in result
    assert "export" in result


def test_unsupported_format_raises():
    with pytest.raises(ExportError, match="Unsupported"):
        export_env({"A": "1"}, "xml")


def test_empty_env_json():
    result = export_env({}, "json")
    assert json.loads(result) == {}


def test_empty_env_dotenv():
    result = export_env({}, "dotenv")
    assert result == ""
