"""Tests for the search CLI command."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envdiff.search_cli import search_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_no_match_exits_0(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(search_cmd, ["MISSING", f])
    assert result.exit_code == 0
    assert "No matches" in result.output


def test_match_exits_1(runner, tmp_path):
    f = write(tmp_path, ".env", "DB_HOST=localhost\n")
    result = runner.invoke(search_cmd, ["DB_HOST", f])
    assert result.exit_code == 1
    assert "DB_HOST" in result.output


def test_invalid_pattern_exits_2(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(search_cmd, ["[bad", f])
    assert result.exit_code == 2


def test_no_colour_flag(runner, tmp_path):
    f = write(tmp_path, ".env", "API_KEY=secret\n")
    result = runner.invoke(search_cmd, ["--no-colour", "API_KEY", f])
    assert "\033[" not in result.output


def test_keys_only_flag(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=foo_val\nBAR=baz\n")
    result = runner.invoke(search_cmd, ["--no-values", "foo", f])
    assert "FOO" in result.output
    # BAR value does not contain 'foo', so only FOO key match
    assert result.exit_code == 1
