"""Tests for env_diff_leaderboard and leaderboard_formatter."""
import pytest

from envdiff.env_diff_leaderboard import (
    LeaderboardEntry,
    LeaderboardResult,
    build_leaderboard,
)
from envdiff.leaderboard_formatter import format_leaderboard


_BASE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "false"}


def test_empty_targets_returns_empty_result():
    result = build_leaderboard(_BASE, {}, base_name="prod")
    assert result.entries == []
    assert result.winner is None
    assert result.base_name == "prod"


def test_identical_target_scores_100():
    result = build_leaderboard(_BASE, {"staging": dict(_BASE)})
    assert len(result.entries) == 1
    entry = result.entries[0]
    assert entry.score == 100
    assert entry.grade == "A+"
    assert entry.total_issues == 0


def test_missing_key_reduces_score():
    target = {"HOST": "localhost", "PORT": "5432"}  # missing DEBUG
    result = build_leaderboard(_BASE, {"dev": target})
    entry = result.entries[0]
    assert entry.score < 100
    assert "DEBUG" in entry.missing_in_target


def test_entries_sorted_by_score_descending():
    perfect = dict(_BASE)
    partial = {"HOST": "localhost"}
    result = build_leaderboard(
        _BASE,
        {"dev": partial, "staging": perfect},
    )
    assert result.entries[0].name == "staging"
    assert result.entries[1].name == "dev"


def test_winner_is_first_entry():
    result = build_leaderboard(
        _BASE,
        {"a": dict(_BASE), "b": {"HOST": "localhost"}},
    )
    assert result.winner is not None
    assert result.winner.name == "a"


def test_mismatch_recorded_when_compare_values_enabled():
    target = {"HOST": "remotehost", "PORT": "5432", "DEBUG": "false"}
    result = build_leaderboard(_BASE, {"qa": target}, compare_values=True)
    entry = result.entries[0]
    assert "HOST" in entry.mismatched


def test_mismatch_not_recorded_when_compare_values_disabled():
    target = {"HOST": "remotehost", "PORT": "5432", "DEBUG": "false"}
    result = build_leaderboard(_BASE, {"qa": target}, compare_values=False)
    entry = result.entries[0]
    assert entry.mismatched == []


def test_format_leaderboard_no_entries():
    result = LeaderboardResult(base_name="prod")
    output = format_leaderboard(result)
    assert "No targets" in output


def test_format_leaderboard_shows_names_and_scores():
    result = build_leaderboard(
        _BASE,
        {"staging": dict(_BASE), "dev": {"HOST": "localhost"}},
    )
    output = format_leaderboard(result, no_colour=True)
    assert "staging" in output
    assert "dev" in output
    assert "100%" in output


def test_format_leaderboard_shows_base_name():
    result = build_leaderboard(_BASE, {"x": dict(_BASE)}, base_name="production")
    output = format_leaderboard(result)
    assert "production" in output
