"""Tests for env_diff_context and context_formatter."""
import pytest

from envdiff.comparator import compare_envs
from envdiff.context_formatter import format_context_diff
from envdiff.env_diff_context import ContextDiffResult, build_context_diff


def _diff(base, target, check_values=True):
    return compare_envs(base, target, check_values=check_values)


# ---------------------------------------------------------------------------
# build_context_diff
# ---------------------------------------------------------------------------

def test_no_changes_returns_empty_result():
    env = {"A": "1", "B": "2"}
    diff = _diff(env, env)
    result = build_context_diff(env, env, diff)
    assert result.is_empty()


def test_missing_in_target_creates_block():
    base = {"A": "1", "B": "2", "C": "3"}
    target = {"A": "1", "C": "3"}
    diff = _diff(base, target)
    result = build_context_diff(base, target, diff, context=1)
    assert len(result.blocks) == 1
    block = result.blocks[0]
    assert block.key == "B"
    assert block.change_type == "missing_in_target"
    assert block.base_value == "2"


def test_context_lines_populated():
    base = {"X": "x", "MISSING": "m", "Z": "z"}
    target = {"X": "x", "Z": "z"}
    diff = _diff(base, target)
    result = build_context_diff(base, target, diff, context=1)
    block = result.blocks[0]
    assert ("X", "x") in block.before
    assert ("Z", "z") in block.after


def test_mismatch_block_has_both_values():
    base = {"PORT": "8000"}
    target = {"PORT": "9000"}
    diff = _diff(base, target)
    result = build_context_diff(base, target, diff)
    block = result.blocks[0]
    assert block.change_type == "mismatch"
    assert block.base_value == "8000"
    assert block.target_value == "9000"


def test_missing_in_base_block():
    base = {"A": "1"}
    target = {"A": "1", "NEW": "n"}
    diff = _diff(base, target)
    result = build_context_diff(base, target, diff)
    assert any(b.change_type == "missing_in_base" for b in result.blocks)


def test_context_zero_lines():
    base = {"A": "1", "B": "2", "C": "3"}
    target = {"A": "1", "C": "3"}
    diff = _diff(base, target)
    result = build_context_diff(base, target, diff, context=0)
    block = result.blocks[0]
    assert block.before == []
    assert block.after == []


# ---------------------------------------------------------------------------
# format_context_diff
# ---------------------------------------------------------------------------

def test_format_empty_result():
    result = ContextDiffResult(blocks=[])
    assert "No differences" in format_context_diff(result)


def test_format_shows_key_and_label():
    base = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    target = {"DB_HOST": "localhost"}
    diff = _diff(base, target)
    result = build_context_diff(base, target, diff)
    output = format_context_diff(result, no_color=True)
    assert "DB_PORT" in output
    assert "missing in target" in output


def test_format_no_color_strips_ansi():
    base = {"KEY": "val"}
    target = {}
    diff = _diff(base, target)
    result = build_context_diff(base, target, diff)
    output = format_context_diff(result, no_color=True)
    assert "\033[" not in output


def test_format_mismatch_shows_values():
    base = {"SECRET": "abc"}
    target = {"SECRET": "xyz"}
    diff = _diff(base, target)
    result = build_context_diff(base, target, diff)
    output = format_context_diff(result, no_color=True)
    assert "abc" in output
    assert "xyz" in output
