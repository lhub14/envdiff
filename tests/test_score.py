"""Tests for envdiff.score and envdiff.score_formatter."""
from __future__ import annotations

import pytest
from click.testing import CliRunner

from envdiff.comparator import compare_envs, DiffResult
from envdiff.score import compute_score, ScoreResult
from envdiff.score_formatter import format_score
from envdiff.score_cli import score_cmd


def _diff(**kwargs) -> DiffResult:
    defaults = dict(missing_in_target={}, missing_in_base={}, mismatched={})
    defaults.update(kwargs)
    return DiffResult(**defaults)


def test_perfect_score():
    base = {"A": "1", "B": "2"}
    diff = _diff()
    r = compute_score(base, diff)
    assert r.score == 100.0
    assert r.grade == "A"


def test_missing_key_reduces_score():
    base = {"A": "1", "B": "2", "C": "3", "D": "4", "E": "5"}
    diff = _diff(missing_in_target={"A": "1"})
    r = compute_score(base, diff)
    assert r.score < 100.0
    assert r.missing_in_target == 1


def test_mismatch_reduces_score():
    base = {"A": "1", "B": "2"}
    diff = _diff(mismatched={"A": ("1", "x")})
    r = compute_score(base, diff)
    assert r.score < 100.0
    assert r.mismatched == 1


def test_empty_base_returns_100():
    r = compute_score({}, _diff())
    assert r.score == 100.0
    assert r.grade == "A"


def test_grade_f_on_all_missing():
    base = {k: str(i) for i, k in enumerate("ABCDEFGHIJ")}
    diff = _diff(missing_in_target=dict(base))
    r = compute_score(base, diff)
    assert r.grade == "F"


def test_format_score_contains_grade():
    r = ScoreResult(total_keys=5, missing_in_target=0, missing_in_base=0, mismatched=0, score=100.0, grade="A")
    out = format_score(r, colour=False)
    assert "[A]" in out
    assert "100.0" in out


# --- CLI ---

def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_cli_perfect_score(tmp_path):
    base = _write(tmp_path, ".env.base", "A=1\nB=2\n")
    target = _write(tmp_path, ".env.target", "A=1\nB=2\n")
    result = CliRunner().invoke(score_cmd, [base, target, "--no-colour"])
    assert result.exit_code == 0
    assert "100.0" in result.output


def test_cli_fail_below(tmp_path):
    base = _write(tmp_path, ".env.base", "A=1\nB=2\nC=3\nD=4\nE=5\n")
    target = _write(tmp_path, ".env.target", "A=1\n")
    result = CliRunner().invoke(score_cmd, [base, target, "--no-colour", "--fail-below", "90"])
    assert result.exit_code == 1


def test_cli_bad_file_exits_2(tmp_path):
    base = _write(tmp_path, ".env.base", "A=1\n")
    result = CliRunner().invoke(score_cmd, [base, "/nonexistent/.env"])
    assert result.exit_code != 0
