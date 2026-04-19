"""Tests for envdiff.env_search."""
from __future__ import annotations

import pytest

from envdiff.env_search import SearchResult, has_matches, search_envs


def write_env(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_no_matches_returns_empty(tmp_path):
    f = write_env(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    result = search_envs({"env": f}, "MISSING")
    assert not has_matches(result)
    assert result.matches == []


def test_key_match(tmp_path):
    f = write_env(tmp_path, ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    result = search_envs({"env": f}, "DB_HOST")
    assert len(result.matches) == 1
    assert result.matches[0].key == "DB_HOST"
    assert result.matches[0].match_type == "key"


def test_value_match(tmp_path):
    f = write_env(tmp_path, ".env", "HOST=localhost\nPORT=5432\n")
    result = search_envs({"env": f}, "localhost")
    assert len(result.matches) == 1
    assert result.matches[0].match_type == "value"


def test_both_match(tmp_path):
    f = write_env(tmp_path, ".env", "NAME=name_value\n")
    result = search_envs({"env": f}, "name")
    assert result.matches[0].match_type == "both"


def test_case_insensitive_default(tmp_path):
    f = write_env(tmp_path, ".env", "API_KEY=secret\n")
    result = search_envs({"env": f}, "api_key")
    assert has_matches(result)


def test_case_sensitive_no_match(tmp_path):
    f = write_env(tmp_path, ".env", "API_KEY=secret\n")
    result = search_envs({"env": f}, "api_key", case_sensitive=True)
    assert not has_matches(result)


def test_search_keys_only(tmp_path):
    f = write_env(tmp_path, ".env", "FOO=bar\nBAR=foo\n")
    result = search_envs({"env": f}, "foo", search_values=False)
    assert all(m.match_type == "key" for m in result.matches)
    assert len(result.matches) == 1


def test_search_values_only(tmp_path):
    f = write_env(tmp_path, ".env", "FOO=bar\nBAR=foo\n")
    result = search_envs({"env": f}, "foo", search_keys=False)
    assert all(m.match_type == "value" for m in result.matches)


def test_multiple_files(tmp_path):
    f1 = write_env(tmp_path, "a.env", "TOKEN=abc\n")
    f2 = write_env(tmp_path, "b.env", "TOKEN=xyz\n")
    result = search_envs({"a": f1, "b": f2}, "TOKEN")
    files = {m.file for m in result.matches}
    assert files == {"a", "b"}


def test_invalid_pattern_raises(tmp_path):
    f = write_env(tmp_path, ".env", "FOO=bar\n")
    with pytest.raises(ValueError, match="Invalid pattern"):
        search_envs({"env": f}, "[invalid")
