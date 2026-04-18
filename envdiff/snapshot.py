"""Point-in-time snapshot of an env file for later comparison."""
from __future__ import annotations

import json
import datetime
from pathlib import Path
from typing import Dict, List

from envdiff.parser import parse_env_file


class SnapshotError(Exception):
    pass


def _now_iso() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"


def take_snapshot(env_path: str | Path) -> dict:
    """Parse *env_path* and return a snapshot dict with metadata."""
    path = Path(env_path)
    if not path.exists():
        raise SnapshotError(f"File not found: {path}")
    env = parse_env_file(path)
    return {
        "file": str(path),
        "captured_at": _now_iso(),
        "keys": sorted(env.keys()),
        "values": env,
    }


def save_snapshot(snapshot: dict, store: str | Path) -> None:
    """Append *snapshot* to a JSON-lines store file."""
    store = Path(store)
    store.parent.mkdir(parents=True, exist_ok=True)
    with store.open("a") as fh:
        fh.write(json.dumps(snapshot) + "\n")


def load_snapshots(store: str | Path) -> List[dict]:
    """Return all snapshots from *store*, oldest first."""
    store = Path(store)
    if not store.exists():
        return []
    snapshots = []
    for line in store.read_text().splitlines():
        line = line.strip()
        if line:
            snapshots.append(json.loads(line))
    return snapshots


def diff_snapshots(older: dict, newer: dict) -> Dict[str, object]:
    """Return a simple diff between two snapshots."""
    old_vals: Dict[str, str] = older["values"]
    new_vals: Dict[str, str] = newer["values"]
    added = {k: new_vals[k] for k in new_vals if k not in old_vals}
    removed = {k: old_vals[k] for k in old_vals if k not in new_vals}
    changed = {
        k: {"old": old_vals[k], "new": new_vals[k]}
        for k in old_vals
        if k in new_vals and old_vals[k] != new_vals[k]
    }
    return {"added": added, "removed": removed, "changed": changed}
