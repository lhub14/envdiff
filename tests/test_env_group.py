"""Tests for envdiff.env_group."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envdiff.env_group import group_by_prefix, format_group_result, GroupResult
from envdiff.group_cli import group_cmd


ENV = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_NAME": "myapp",
    "APP_DEBUG": "true",
    "SECRET_KEY": "abc",
}


def test_basic_grouping():
    result = group_by_prefix(ENV, ["DB_", "APP_"])
    assert sorted(result.groups["DB_"]) == ["DB_HOST", "DB_PORT"]
    assert sorted(result.groups["APP_"]) == ["APP_DEBUG", "APP_NAME"]
    assert result.ungrouped == ["SECRET_KEY"]


def test_strip_prefix():
    result = group_by_prefix(ENV, ["DB_"], strip_prefix=True)
    assert sorted(result.groups["DB_"]) == ["HOST", "PORT"]


def test_no_match_all_ungrouped():
    result = group_by_prefix(ENV, ["NOPE_"])
    assert result.groups["NOPE_"] == []
    assert len(result.ungrouped) == len(ENV)


def test_empty_env():
    result = group_by_prefix({}, ["DB_"])
    assert result.groups["DB_"] == []
    assert result.ungrouped == []


def test_format_output_contains_prefix():
    result = group_by_prefix(ENV, ["DB_"])
    out = format_group_result(result)
    assert "[DB_]" in out
    assert "DB_HOST" in out


def test_format_no_keys():
    out = format_group_result(GroupResult())
    assert out == "No keys."


# --- CLI tests ---

@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_cli_groups_keys(runner, tmp_path):
    f = write(tmp_path, ".env", "DB_HOST=localhost\nDB_PORT=5432\nSECRET=x\n")
    result = runner.invoke(group_cmd, [f, "--prefix", "DB_"])
    assert result.exit_code == 0
    assert "DB_HOST" in result.output
    assert "ungrouped" in result.output


def test_cli_strip_flag(runner, tmp_path):
    f = write(tmp_path, ".env", "DB_HOST=localhost\nDB_PORT=5432\n")
    result = runner.invoke(group_cmd, [f, "--prefix", "DB_", "--strip"])
    assert result.exit_code == 0
    assert "HOST" in result.output
    assert "DB_HOST" not in result.output


def test_cli_bad_file(runner, tmp_path):
    result = runner.invoke(group_cmd, ["nonexistent.env", "--prefix", "X_"])
    assert result.exit_code != 0
