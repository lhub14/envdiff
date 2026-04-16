"""Tests for envdiff.audit_formatter module."""
from envdiff.audit import AuditEntry
from envdiff.audit_formatter import format_audit_log


def _entry(**kwargs):
    defaults = dict(
        timestamp="2024-01-01T00:00:00+00:00",
        base=".env",
        target=".env.prod",
        missing_in_target=[],
        missing_in_base=[],
        mismatched=[],
        has_diff=False,
    )
    defaults.update(kwargs)
    return AuditEntry(**defaults)


def test_empty_list():
    assert format_audit_log([]) == "No audit entries found."


def test_ok_entry():
    out = format_audit_log([_entry()])
    assert "OK" in out
    assert ".env.prod" in out


def test_diff_entry_shows_missing():
    e = _entry(missing_in_target=["SECRET"], has_diff=True)
    out = format_audit_log([e])
    assert "DIFF" in out
    assert "SECRET" in out
    assert "missing in target" in out


def test_mismatched_shown():
    e = _entry(mismatched=["PORT"], has_diff=True)
    out = format_audit_log([e])
    assert "PORT" in out
    assert "mismatched" in out


def test_multiple_entries():
    entries = [_entry(), _entry(missing_in_base=["FOO"], has_diff=True)]
    out = format_audit_log(entries)
    assert out.count("2024-01-01") == 2
