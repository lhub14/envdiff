"""Tests for the watch CLI command."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envdiff.watch_cli import watch_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_watch_initial_diff_no_diff(runner: CliRunner, tmp_path: Path) -> None:
    base = write(tmp_path, "base.env", "A=1\nB=2\n")
    target = write(tmp_path, "target.env", "A=1\nB=2\n")
    with patch("envdiff.watch_cli.watch_files") as mock_watch:
        result = runner.invoke(watch_cmd, [str(base), str(target), "--interval", "0.01"])
    assert result.exit_code == 0
    assert "Watching" in result.output
    mock_watch.assert_called_once()


def test_watch_initial_diff_shows_missing(runner: CliRunner, tmp_path: Path) -> None:
    base = write(tmp_path, "base.env", "A=1\nB=2\n")
    target = write(tmp_path, "target.env", "A=1\n")
    with patch("envdiff.watch_cli.watch_files"):
        result = runner.invoke(watch_cmd, [str(base), str(target)])
    assert "B" in result.output


def test_watch_keyboard_interrupt_exits_cleanly(runner: CliRunner, tmp_path: Path) -> None:
    base = write(tmp_path, "base.env", "A=1\n")
    target = write(tmp_path, "target.env", "A=1\n")
    with patch("envdiff.watch_cli.watch_files", side_effect=KeyboardInterrupt):
        result = runner.invoke(watch_cmd, [str(base), str(target)])
    assert result.exit_code == 0
    assert "stopped" in result.output
