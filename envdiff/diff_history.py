"""Track and retrieve historical diff results across runs."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_STORE = Path(".envdiff_history.json")


class HistoryError(Exception):
    pass


@dataclass
class HistoryEntry:
    timestamp: str
    base: str
    target: str
    missing_in_target: List[str]
    missing_in_base: List[str]
    mismatched: List[str]
    had_diff: bool


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_entry(base: str, target: str, diff) -> HistoryEntry:
    """Create a HistoryEntry from a DiffResult."""
    return HistoryEntry(
        timestamp=_now_iso(),
        base=base,
        target=target,
        missing_in_target=list(diff.missing_in_target),
        missing_in_base=list(diff.missing_in_base),
        mismatched=list(diff.mismatched.keys()),
        had_diff=(
            bool(diff.missing_in_target)
            or bool(diff.missing_in_base)
            or bool(diff.mismatched)
        ),
    )


def append_entry(entry: HistoryEntry, store: Path = DEFAULT_STORE) -> None:
    entries = _load_raw(store)
    entries.append(asdict(entry))
    store.write_text(json.dumps(entries, indent=2))


def load_history(store: Path = DEFAULT_STORE) -> List[HistoryEntry]:
    raw = _load_raw(store)
    return [HistoryEntry(**r) for r in raw]


def _load_raw(store: Path):
    if not store.exists():
        return []
    try:
        return json.loads(store.read_text())
    except json.JSONDecodeError as exc:
        raise HistoryError(f"Corrupt history file: {store}") from exc


def clear_history(store: Path = DEFAULT_STORE) -> int:
    if not store.exists():
        return 0
    entries = load_history(store)
    count = len(entries)
    store.unlink()
    return count


def last_entry(store: Path = DEFAULT_STORE) -> Optional[HistoryEntry]:
    entries = load_history(store)
    return entries[-1] if entries else None
