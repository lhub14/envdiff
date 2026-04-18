"""Tests for envdiff.graph_cli."""
import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envdiff.graph_cli import graph_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_shared_keys_shown(runner, tmp_path):
    a = write(tmp_path, "a.env", "HOST=localhost\nPORT=5432\n")
    b = write(tmp_path, "b.env", "HOST=prod\nPORT=5432\n")
    result = runner.invoke(graph_cmd, ["--no-color", a, b])
    assert result.exit_code == 0
    assert "HOST" in result.output
    assert "PORT" in result.output
    assert "Universal" in result.output


def test_unique_key_shown(runner, tmp_path):
    a = write(tmp_path, "a.env", "HOST=localhost\nDEBUG=true\n")
    b = write(tmp_path, "b.env", "HOST=prod\n")
    result = runner.invoke(graph_cmd, ["--no-color", a, b])
    assert result.exit_code == 0
    assert "DEBUG" in result.output
    assert "Unique" in result.output


def test_json_output_structure(runner, tmp_path):
    a = write(tmp_path, "a.env", "X=1\nY=2\n")
    b = write(tmp_path, "b.env", "X=1\nZ=3\n")
    result = runner.invoke(graph_cmd, ["--json", a, b])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "universal" in data
    assert "partial" in data
    assert "unique" in data
    assert "shared_ratio" in data
    assert "X" in data["universal"]


def test_missing_file_exits_2(runner, tmp_path):
    result = runner.invoke(graph_cmd, ["/nonexistent/file.env"])
    assert result.exit_code == 2


def test_shared_ratio_in_output(runner, tmp_path):
    a = write(tmp_path, "a.env", "K=1\n")
    b = write(tmp_path, "b.env", "K=1\n")
    result = runner.invoke(graph_cmd, ["--no-color", a, b])
    assert "100%" in result.output
