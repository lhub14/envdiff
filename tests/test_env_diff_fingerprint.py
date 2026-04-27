"""Tests for envdiff.env_diff_fingerprint."""
from __future__ import annotations

import pytest

from envdiff.env_diff_fingerprint import (
    FingerprintResult,
    compute_fingerprints,
    identical,
    same_shape,
)
from envdiff.fingerprint_formatter import format_fingerprint_result


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "prod.example.com", "PORT": "5432", "DEBUG": "false"}  # same keys, diff values
ENV_C = {"HOST": "localhost", "PORT": "5432"}  # subset of keys
ENV_D = dict(ENV_A)  # identical to A


# ---------------------------------------------------------------------------
# compute_fingerprints
# ---------------------------------------------------------------------------

def test_empty_input_returns_empty_result():
    result = compute_fingerprints({})
    assert result.files == {}
    assert result.shape_groups == {}


def test_single_file_has_fingerprint():
    result = compute_fingerprints({"a.env": ENV_A})
    assert "a.env" in result.files
    assert len(result.files["a.env"]) == 12


def test_identical_envs_produce_same_fingerprint():
    result = compute_fingerprints({"a.env": ENV_A, "d.env": ENV_D})
    assert result.files["a.env"] == result.files["d.env"]


def test_different_values_produce_different_fingerprints():
    result = compute_fingerprints({"a.env": ENV_A, "b.env": ENV_B})
    assert result.files["a.env"] != result.files["b.env"]


def test_shape_group_detected_when_keys_match():
    result = compute_fingerprints({"a.env": ENV_A, "b.env": ENV_B})
    # A and B have same keys → should share a shape group
    assert len(result.shape_groups) == 1
    members = list(result.shape_groups.values())[0]
    assert "a.env" in members
    assert "b.env" in members


def test_no_shape_group_when_keys_differ():
    result = compute_fingerprints({"a.env": ENV_A, "c.env": ENV_C})
    assert result.shape_groups == {}


def test_fingerprint_is_order_independent():
    env1 = {"B": "2", "A": "1"}
    env2 = {"A": "1", "B": "2"}
    r1 = compute_fingerprints({"x": env1})
    r2 = compute_fingerprints({"x": env2})
    assert r1.files["x"] == r2.files["x"]


# ---------------------------------------------------------------------------
# identical / same_shape helpers
# ---------------------------------------------------------------------------

def test_identical_true_for_same_content():
    result = compute_fingerprints({"a.env": ENV_A, "d.env": ENV_D})
    assert identical(result, "a.env", "d.env") is True


def test_identical_false_for_different_values():
    result = compute_fingerprints({"a.env": ENV_A, "b.env": ENV_B})
    assert identical(result, "a.env", "b.env") is False


def test_same_shape_true_when_keys_match():
    result = compute_fingerprints({"a.env": ENV_A, "b.env": ENV_B})
    assert same_shape(result, "a.env", "b.env") is True


def test_same_shape_false_when_keys_differ():
    result = compute_fingerprints({"a.env": ENV_A, "c.env": ENV_C})
    assert same_shape(result, "a.env", "c.env") is False


# ---------------------------------------------------------------------------
# formatter smoke tests
# ---------------------------------------------------------------------------

def test_format_empty_result():
    result = FingerprintResult()
    out = format_fingerprint_result(result, colour=False)
    assert "no files" in out


def test_format_shows_fingerprints():
    result = compute_fingerprints({"a.env": ENV_A, "b.env": ENV_B})
    out = format_fingerprint_result(result, colour=False)
    assert "a.env" in out
    assert "b.env" in out
    assert "Shared Key Shapes" in out


def test_format_no_shared_shape_message():
    result = compute_fingerprints({"a.env": ENV_A, "c.env": ENV_C})
    out = format_fingerprint_result(result, colour=False)
    assert "No files share" in out
