"""Tests for envdiff.graph."""
from envdiff.graph import build_graph, shared_ratio, GraphResult


A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
B = {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc"}
C = {"HOST": "staging", "PORT": "5432"}


def test_empty_envs_returns_empty_result():
    r = build_graph({})
    assert r.universal == frozenset()
    assert r.unique == {}
    assert r.partial == {}


def test_single_env_all_keys_are_universal():
    r = build_graph({"dev": A})
    assert r.universal == frozenset(A.keys())
    assert r.unique == {}
    assert r.partial == {}


def test_universal_keys_present_in_all():
    r = build_graph({"a": A, "b": B, "c": C})
    assert "HOST" in r.universal
    assert "PORT" in r.universal


def test_unique_key_only_in_one_file():
    r = build_graph({"a": A, "b": B, "c": C})
    assert "DEBUG" in r.unique
    assert r.unique["DEBUG"] == "a"
    assert "SECRET" in r.unique
    assert r.unique["SECRET"] == "b"


def test_partial_key_in_some_files():
    envs = {
        "x": {"A": "1", "B": "2"},
        "y": {"A": "1", "C": "3"},
        "z": {"A": "1"},
    }
    r = build_graph(envs)
    assert "A" in r.universal
    assert "B" in r.partial
    assert "C" in r.partial
    assert r.partial["B"] == {"x"}
    assert r.partial["C"] == {"y"}


def test_shared_ratio_perfect():
    envs = {"a": {"K": "1"}, "b": {"K": "2"}}
    r = build_graph(envs)
    assert shared_ratio(r, 2) == 1.0


def test_shared_ratio_none_shared():
    envs = {"a": {"X": "1"}, "b": {"Y": "2"}}
    r = build_graph(envs)
    assert shared_ratio(r, 2) == 0.0


def test_shared_ratio_partial():
    envs = {"a": {"X": "1", "Z": "3"}, "b": {"Y": "2", "Z": "3"}}
    r = build_graph(envs)
    # Z is universal (1 of 3 keys)
    ratio = shared_ratio(r, 2)
    assert 0.0 < ratio < 1.0
