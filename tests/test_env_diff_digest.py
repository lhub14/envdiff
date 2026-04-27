"""Tests for envdiff.env_diff_digest and envdiff.digest_formatter."""
from __future__ import annotations

import json

import pytest

from envdiff.comparator import DiffResult
from envdiff.env_diff_digest import (
    DigestResult,
    compute_digest,
    digest_diff,
    digest_env,
)
from envdiff.digest_formatter import digest_result_to_json, format_digest_result


# ---------------------------------------------------------------------------
# digest_env
# ---------------------------------------------------------------------------

def test_digest_env_is_deterministic():
    env = {"FOO": "bar", "BAZ": "qux"}
    assert digest_env(env) == digest_env(env)


def test_digest_env_order_independent():
    a = {"FOO": "1", "BAR": "2"}
    b = {"BAR": "2", "FOO": "1"}
    assert digest_env(a) == digest_env(b)


def test_digest_env_changes_with_different_values():
    assert digest_env({"FOO": "a"}) != digest_env({"FOO": "b"})


def test_digest_env_returns_16_char_hex():
    result = digest_env({"K": "v"})
    assert len(result) == 16
    int(result, 16)  # must be valid hex


# ---------------------------------------------------------------------------
# digest_diff
# ---------------------------------------------------------------------------

def _make_diff(**kwargs) -> DiffResult:
    defaults = dict(missing_in_target=[], missing_in_base=[], mismatched={})
    defaults.update(kwargs)
    return DiffResult(**defaults)


def test_digest_diff_empty_is_deterministic():
    d = _make_diff()
    assert digest_diff(d) == digest_diff(d)


def test_digest_diff_changes_with_missing_key():
    clean = _make_diff()
    dirty = _make_diff(missing_in_target=["SECRET"])
    assert digest_diff(clean) != digest_diff(dirty)


def test_digest_diff_order_of_missing_keys_independent():
    d1 = _make_diff(missing_in_target=["A", "B"])
    d2 = _make_diff(missing_in_target=["B", "A"])
    assert digest_diff(d1) == digest_diff(d2)


# ---------------------------------------------------------------------------
# compute_digest
# ---------------------------------------------------------------------------

def test_compute_digest_no_previous_is_changed():
    base = {"K": "v"}
    diff = _make_diff()
    result = compute_digest(base, diff)
    assert result.changed is True


def test_compute_digest_same_as_previous_is_unchanged():
    base = {"K": "v"}
    diff = _make_diff()
    first = compute_digest(base, diff)
    second = compute_digest(base, diff, previous_diff_digest=first.diff_digest)
    assert second.changed is False


def test_compute_digest_includes_target_digest():
    base = {"K": "v"}
    target = {"K": "v", "EXTRA": "x"}
    diff = _make_diff(missing_in_base=["EXTRA"])
    result = compute_digest(base, diff, target_env=target)
    assert result.target_digest is not None
    assert result.target_digest != result.base_digest


def test_compute_digest_no_target_gives_none():
    result = compute_digest({}, _make_diff())
    assert result.target_digest is None


# ---------------------------------------------------------------------------
# formatter
# ---------------------------------------------------------------------------

def test_format_digest_result_contains_digests():
    r = DigestResult(base_digest="aabbccdd11223344", target_digest="1234567890abcdef", diff_digest="deadbeef01234567", changed=True)
    text = format_digest_result(r, colour=False)
    assert "aabbccdd11223344" in text
    assert "1234567890abcdef" in text
    assert "deadbeef01234567" in text
    assert "changed" in text


def test_format_digest_result_unchanged_label():
    r = DigestResult(base_digest="a" * 16, target_digest=None, diff_digest="b" * 16, changed=False)
    text = format_digest_result(r, colour=False)
    assert "unchanged" in text


def test_digest_result_to_json_is_valid():
    r = DigestResult(base_digest="a" * 16, target_digest="b" * 16, diff_digest="c" * 16, changed=False)
    data = json.loads(digest_result_to_json(r))
    assert data["changed"] is False
    assert data["base_digest"] == "a" * 16
