"""Integration tests for baseline CLI commands."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.baseline_cli import baseline_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_save_creates_store(runner: CliRunner, tmp_path: Path) -> None:
    env_file = write(tmp_path, ".env", "KEY=val\nPORT=8080\n")
    store = tmp_path / "store.json"
    result = runner.invoke(baseline_group, ["save", "prod", str(env_file), "--store", str(store)])
    assert result.exit_code == 0
    assert "saved" in result.output
    assert store.exists()
    data = json.loads(store.read_text())
    assert "prod" in data


def test_list_shows_labels(runner: CliRunner, tmp_path: Path) -> None:
    env_file = write(tmp_path, ".env", "A=1\n")
    store = tmp_path / "store.json"
    runner.invoke(baseline_group, ["save", "prod", str(env_file), "--store", str(store)])
    runner.invoke(baseline_group, ["save", "staging", str(env_file), "--store", str(store)])
    result = runner.invoke(baseline_group, ["list", "--store", str(store)])
    assert "prod" in result.output
    assert "staging" in result.output


def test_diff_no_change_exit_0(runner: CliRunner, tmp_path: Path) -> None:
    env_file = write(tmp_path, ".env", "A=1\nB=2\n")
    store = tmp_path / "store.json"
    runner.invoke(baseline_group, ["save", "base", str(env_file), "--store", str(store)])
    result = runner.invoke(baseline_group, ["diff", "base", str(env_file), "--store", str(store)])
    assert result.exit_code == 0


def test_diff_change_exit_1(runner: CliRunner, tmp_path: Path) -> None:
    base_file = write(tmp_path, "base.env", "A=1\nB=2\n")
    new_file = write(tmp_path, "new.env", "A=1\n")
    store = tmp_path / "store.json"
    runner.invoke(baseline_group, ["save", "base", str(base_file), "--store", str(store)])
    result = runner.invoke(baseline_group, ["diff", "base", str(new_file), "--store", str(store)])
    assert result.exit_code == 1


def test_diff_missing_label_error(runner: CliRunner, tmp_path: Path) -> None:
    env_file = write(tmp_path, ".env", "A=1\n")
    store = tmp_path / "store.json"
    store.write_text(json.dumps({}))
    result = runner.invoke(baseline_group, ["diff", "ghost", str(env_file), "--store", str(store)])
    assert result.exit_code != 0
