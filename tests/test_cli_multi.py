"""CLI integration tests for multi-file comparison."""
from pathlib import Path
import pytest
from click.testing import CliRunner

from envdiff.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_multi_no_diff(runner, tmp_path):
    base = write(tmp_path, "base.env", "KEY=val\n")
    t1 = write(tmp_path, "t1.env", "KEY=val\n")
    t2 = write(tmp_path, "t2.env", "KEY=val\n")
    result = runner.invoke(main, [str(base), str(t1), str(t2)])
    assert result.exit_code == 0


def test_multi_diff_exit_code(runner, tmp_path):
    base = write(tmp_path, "base.env", "KEY=val\nMISSING=x\n")
    t1 = write(tmp_path, "t1.env", "KEY=val\n")
    result = runner.invoke(main, [str(base), str(t1)])
    assert result.exit_code != 0


def test_multi_output_contains_targets(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\n")
    t1 = write(tmp_path, "t1.env", "A=1\n")
    t2 = write(tmp_path, "t2.env", "A=2\n")
    result = runner.invoke(main, [str(base), str(t1), str(t2)])
    assert str(t1) in result.output or str(t2) in result.output
