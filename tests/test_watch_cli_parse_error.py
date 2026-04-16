"""Edge-case tests for watch CLI when parse errors occur."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from envdiff.watch_cli import watch_cmd, _run_diff
from envdiff.parser import EnvParseError


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_parse_error_in_run_diff_does_not_raise(tmp_path: Path) -> None:
    base = write(tmp_path, "base.env", "A=1")
    target = write(tmp_path, "target.env", "B=2")
    with patch("envdiff.watch_cli.parse_env_file", side_effect=EnvParseError("bad")):
        # Should not raise; just prints error
        _run_diff(base, target, no_values=False)


def test_watch_bad_base_file_exits(runner: CliRunner, tmp_path: Path) -> None:
    target = write(tmp_path, "target.env", "A=1")
    result = runner.invoke(watch_cmd, [str(tmp_path / "missing.env"), str(target)])
    assert result.exit_code != 0
