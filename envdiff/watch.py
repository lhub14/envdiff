"""File watcher that detects .env file changes and re-runs comparison."""
from __future__ import annotations

import time
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List


@dataclass
class WatchState:
    paths: List[Path]
    mtimes: Dict[str, float] = field(default_factory=dict)

    def snapshot(self) -> Dict[str, float]:
        result = {}
        for p in self.paths:
            try:
                result[str(p)] = p.stat().st_mtime
            except FileNotFoundError:
                result[str(p)] = 0.0
        return result

    def has_changed(self) -> bool:
        current = self.snapshot()
        return current != self.mtimes

    def update(self) -> None:
        self.mtimes = self.snapshot()


def watch_files(
    paths: List[Path],
    callback: Callable[[], None],
    interval: float = 1.0,
    max_cycles: int | None = None,
) -> None:
    """Poll paths and invoke callback whenever any file changes."""
    state = WatchState(paths=paths)
    state.update()
    cycles = 0
    while max_cycles is None or cycles < max_cycles:
        time.sleep(interval)
        if state.has_changed():
            state.update()
            callback()
        cycles += 1
