"""Tests for envdiff.env_prune and envdiff.prune_cli."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.env_prune import has_pruned, prune_env
from envdiff.prune_cli import prune_cmd


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Unit tests for prune_env
# ---------------------------------------------------------------------------

def test_no_stale_keys_returns_empty_pruned(tmp_path):
    src = write_env(tmp_path, "src.env", "A=1\nB=2\n")
    ref = write_env(tmp_path, "ref.env", "A=1\nB=2\nC=3\n")
    result = prune_env(src, [ref], dry_run=True)
    assert result.pruned == []
    assert not has_pruned(result)


def test_stale_key_detected(tmp_path):
    src = write_env(tmp_path, "src.env", "A=1\nSTALE=old\n")
    ref = write_env(tmp_path, "ref.env", "A=1\n")
    result = prune_env(src, [ref], dry_run=True)
    assert "STALE" in result.pruned
    assert has_pruned(result)


def test_dry_run_does_not_modify_file(tmp_path):
    original = "A=1\nSTALE=old\n"
    src = write_env(tmp_path, "src.env", original)
    ref = write_env(tmp_path, "ref.env", "A=1\n")
    prune_env(src, [ref], dry_run=True)
    assert src.read_text(encoding="utf-8") == original


def test_write_mode_removes_stale_key(tmp_path):
    src = write_env(tmp_path, "src.env", "A=1\nSTALE=old\n")
    ref = write_env(tmp_path, "ref.env", "A=1\n")
    prune_env(src, [ref], dry_run=False)
    remaining = src.read_text(encoding="utf-8")
    assert "STALE" not in remaining
    assert "A=1" in remaining


def test_key_in_any_reference_is_kept(tmp_path):
    src = write_env(tmp_path, "src.env", "A=1\nB=2\n")
    ref1 = write_env(tmp_path, "ref1.env", "A=1\n")
    ref2 = write_env(tmp_path, "ref2.env", "B=2\n")
    result = prune_env(src, [ref1, ref2], dry_run=True)
    assert result.pruned == []


def test_comments_and_blanks_preserved(tmp_path):
    src = write_env(tmp_path, "src.env", "# header\n\nA=1\nSTALE=x\n")
    ref = write_env(tmp_path, "ref.env", "A=1\n")
    result = prune_env(src, [ref], dry_run=True)
    assert any(line.startswith("#") for line in result.output_lines)
    assert "STALE" in result.pruned


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture
def runner():
    return CliRunner()


def test_cli_no_stale_exit_0(tmp_path, runner):
    src = write_env(tmp_path, "src.env", "A=1\n")
    ref = write_env(tmp_path, "ref.env", "A=1\n")
    result = runner.invoke(prune_cmd, [str(src), str(ref)])
    assert result.exit_code == 0


def test_cli_stale_key_exit_1(tmp_path, runner):
    src = write_env(tmp_path, "src.env", "A=1\nSTALE=x\n")
    ref = write_env(tmp_path, "ref.env", "A=1\n")
    result = runner.invoke(prune_cmd, ["--dry-run", str(src), str(ref)])
    assert result.exit_code == 1
    assert "STALE" in result.output


def test_cli_quiet_suppresses_output(tmp_path, runner):
    src = write_env(tmp_path, "src.env", "A=1\nSTALE=x\n")
    ref = write_env(tmp_path, "ref.env", "A=1\n")
    result = runner.invoke(prune_cmd, ["--dry-run", "--quiet", str(src), str(ref)])
    assert result.exit_code == 1
    assert result.output.strip() == ""
