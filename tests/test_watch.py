"""Tests for envdiff.watch module."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from envdiff.watch import WatchState, watch_files


def test_snapshot_returns_mtime(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("A=1")
    state = WatchState(paths=[f])
    snap = state.snapshot()
    assert str(f) in snap
    assert snap[str(f)] > 0


def test_missing_file_returns_zero(tmp_path: Path) -> None:
    f = tmp_path / "missing.env"
    state = WatchState(paths=[f])
    snap = state.snapshot()
    assert snap[str(f)] == 0.0


def test_has_changed_after_write(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("A=1")
    state = WatchState(paths=[f])
    state.update()
    assert not state.has_changed()
    time.sleep(0.05)
    f.write_text("A=2")
    # Force mtime difference
    new_mtime = f.stat().st_mtime + 1
    import os
    os.utime(f, (new_mtime, new_mtime))
    assert state.has_changed()


def test_update_clears_changed(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("A=1")
    state = WatchState(paths=[f])
    state.update()
    state.update()
    assert not state.has_changed()


def test_watch_files_calls_callback(tmp_path: Path) -> None:
    f = tmp_path / ".env"
    f.write_text("A=1")

    calls: list[int] = []

    def on_change() -> None:
        calls.append(1)

    import os
    # Modify file mtime before watch starts so first poll sees a change
    state_pre = WatchState(paths=[f])
    state_pre.update()
    new_mtime = f.stat().st_mtime + 2
    os.utime(f, (new_mtime, new_mtime))

    watch_files([f], on_change, interval=0.01, max_cycles=2)
    assert len(calls) >= 1
