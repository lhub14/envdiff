"""Tests for envdiff.suggest and envdiff.suggest_formatter."""
import pytest
from envdiff.suggest import suggest_defaults, Suggestion, SuggestResult
from envdiff.suggest_formatter import format_suggest_result


def test_empty_input_returns_empty_result():
    result = suggest_defaults([])
    assert result.suggestions == []
    assert result.unmatched == []


def test_known_key_port_matched():
    result = suggest_defaults(["PORT"])
    assert len(result.suggestions) == 1
    assert result.suggestions[0].key == "PORT"
    assert result.suggestions[0].value == "8080"


def test_suffix_match_app_port():
    result = suggest_defaults(["APP_PORT"])
    assert result.suggestions[0].value == "8080"


def test_debug_flag_suggested_false():
    result = suggest_defaults(["DEBUG"])
    assert result.suggestions[0].value == "false"


def test_unknown_key_goes_to_unmatched():
    result = suggest_defaults(["MY_SECRET_TOKEN"])
    assert result.unmatched == ["MY_SECRET_TOKEN"]
    assert result.suggestions == []


def test_mixed_keys():
    result = suggest_defaults(["DB_PORT", "UNKNOWN_KEY", "LOG_LEVEL"])
    keys = [s.key for s in result.suggestions]
    assert "DB_PORT" in keys
    assert "LOG_LEVEL" in keys
    assert "UNKNOWN_KEY" in result.unmatched


def test_db_port_value():
    result = suggest_defaults(["DB_PORT"])
    assert result.suggestions[0].value == "5432"


def test_timezone_matched():
    result = suggest_defaults(["TZ"])
    assert result.suggestions[0].value == "UTC"


def test_format_empty_result():
    result = SuggestResult()
    out = format_suggest_result(result, colour=False)
    assert "No missing" in out


def test_format_with_suggestions():
    result = suggest_defaults(["PORT", "DEBUG"])
    out = format_suggest_result(result, colour=False)
    assert "PORT=8080" in out
    assert "DEBUG=false" in out


def test_format_unmatched_shown():
    result = suggest_defaults(["WEIRD_SECRET"])
    out = format_suggest_result(result, colour=False)
    assert "WEIRD_SECRET" in out
    assert "No suggestion available" in out


def test_format_colour_contains_ansi():
    result = suggest_defaults(["PORT"])
    out = format_suggest_result(result, colour=True)
    assert "\033[" in out
