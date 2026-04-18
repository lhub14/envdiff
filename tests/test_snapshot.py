"""Tests for envdiff.snapshot."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envdiff.snapshot import (
    SnapshotError,
    take_snapshot,
    save_snapshot,
    load_snapshots,
    diff_snapshots,
)
from envdiff.snapshot_cli import snapshot_group


def write_env(path: Path, content: str) -> None:
    path.write_text(content)


def test_take_snapshot_keys(tmp_path):
    f = tmp_path / ".env"
    write_env(f, "FOO=bar\nBAZ=qux\n")
    snap = take_snapshot(f)
    assert set(snap["keys"]) == {"FOO", "BAZ"}
    assert snap["values"]["FOO"] == "bar"


def test_take_snapshot_missing_file(tmp_path):
    with pytest.raises(SnapshotError):
        take_snapshot(tmp_path / "missing.env")


def test_save_and_load(tmp_path):
    f = tmp_path / ".env"
    store = tmp_path / "snaps.jsonl"
    write_env(f, "A=1\nB=2\n")
    snap = take_snapshot(f)
    save_snapshot(snap, store)
    save_snapshot(snap, store)
    loaded = load_snapshots(store)
    assert len(loaded) == 2


def test_load_missing_store(tmp_path):
    assert load_snapshots(tmp_path / "no.jsonl") == []


def test_diff_snapshots_added_removed_changed():
    older = {"values": {"A": "1", "B": "2"}, "keys": ["A", "B"]}
    newer = {"values": {"A": "99", "C": "3"}, "keys": ["A", "C"]}
    result = diff_snapshots(older, newer)
    assert "C" in result["added"]
    assert "B" in result["removed"]
    assert "A" in result["changed"]
    assert result["changed"]["A"] == {"old": "1", "new": "99"}


def test_diff_snapshots_no_changes():
    snap = {"values": {"X": "y"}, "keys": ["X"]}
    result = diff_snapshots(snap, snap)
    assert result == {"added": {}, "removed": {}, "changed": {}}


def test_cli_capture_and_list(tmp_path):
    runner = CliRunner()
    env = tmp_path / ".env"
    store = tmp_path / "store.jsonl"
    write_env(env, "KEY=val\n")
    r = runner.invoke(snapshot_group, ["capture", str(env), "--store", str(store)])
    assert r.exit_code == 0
    assert "Snapshot captured" in r.output
    r2 = runner.invoke(snapshot_group, ["list", "--store", str(store)])
    assert "KEY" in r2.output or ".env" in r2.output


def test_cli_diff_json(tmp_path):
    runner = CliRunner()
    store = tmp_path / "store.jsonl"
    snap1 = {"file": "a", "captured_at": "t1", "keys": ["A"], "values": {"A": "1"}}
    snap2 = {"file": "a", "captured_at": "t2", "keys": ["A"], "values": {"A": "2"}}
    save_snapshot(snap1, store)
    save_snapshot(snap2, store)
    r = runner.invoke(snapshot_group, ["diff", "--store", str(store), "--json"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert "changed" in data
