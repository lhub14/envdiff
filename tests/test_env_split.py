"""Tests for envdiff.env_split and split_cli."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.env_split import split_by_prefix, split_env_file, write_split_files, has_unmatched
from envdiff.split_cli import split_cmd


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_split_by_prefix_basic():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp", "SECRET": "x"}
    result = split_by_prefix(env, ["DB_", "APP_"])
    assert result.groups["DB_"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}
    assert result.groups["APP_"] == {"APP_NAME": "myapp"}
    assert result.unmatched == {"SECRET": "x"}


def test_split_strip_prefix():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = split_by_prefix(env, ["DB_"], strip_prefix=True)
    assert result.groups["DB_"] == {"HOST": "localhost", "PORT": "5432"}


def test_no_unmatched():
    env = {"DB_HOST": "h"}
    result = split_by_prefix(env, ["DB_"])
    assert not has_unmatched(result)


def test_all_unmatched():
    env = {"FOO": "1", "BAR": "2"}
    result = split_by_prefix(env, ["DB_"])
    assert result.unmatched == {"FOO": "1", "BAR": "2"}
    assert result.groups["DB_"] == {}


def test_split_env_file(tmp_path: Path):
    p = write_env(tmp_path, ".env", "DB_HOST=localhost\nAPP_PORT=8000\n")
    result = split_env_file(p, ["DB_", "APP_"])
    assert "DB_HOST" in result.groups["DB_"]
    assert "APP_PORT" in result.groups["APP_"]


def test_write_split_files(tmp_path: Path):
    from envdiff.env_split import SplitResult
    result = SplitResult(
        groups={"DB_": {"DB_HOST": "localhost"}, "APP_": {"APP_PORT": "8000"}},
        unmatched={},
    )
    out = tmp_path / "out"
    written = write_split_files(result, out)
    assert len(written) == 2
    names = {p.name for p in written}
    assert "db_.env" in names
    assert "app_.env" in names


def test_cli_split(tmp_path: Path):
    runner = CliRunner()
    p = write_env(tmp_path, ".env", "DB_HOST=localhost\nAPP_PORT=8000\nSECRET=x\n")
    out = tmp_path / "split"
    res = runner.invoke(split_cmd, [str(p), "--prefix", "DB_", "--prefix", "APP_", "-o", str(out)])
    assert res.exit_code == 0
    assert "wrote" in res.output
    assert "unmatched" in res.output  # SECRET unmatched warning


def test_cli_no_unmatched_warning_suppressed(tmp_path: Path):
    runner = CliRunner()
    p = write_env(tmp_path, ".env", "DB_HOST=localhost\n")
    out = tmp_path / "split"
    res = runner.invoke(
        split_cmd,
        [str(p), "--prefix", "DB_", "-o", str(out), "--no-warn-unmatched"],
    )
    assert res.exit_code == 0
    assert "unmatched" not in res.output
