"""Baseline snapshot: save and diff against a stored .env snapshot."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from envdiff.comparator import DiffResult, compare_envs


class BaselineError(Exception):
    pass


@dataclass
class Baseline:
    label: str
    env: Dict[str, str]
    created_at: str


def save_baseline(label: str, env: Dict[str, str], store_path: Path, created_at: Optional[str] = None) -> Baseline:
    """Persist a baseline snapshot to a JSON store file."""
    from envdiff.audit import _now_iso

    store_path.parent.mkdir(parents=True, exist_ok=True)
    store: dict = {}
    if store_path.exists():
        try:
            store = json.loads(store_path.read_text())
        except json.JSONDecodeError as exc:
            raise BaselineError(f"Corrupt baseline store: {exc}") from exc

    entry = {"label": label, "env": env, "created_at": created_at or _now_iso()}
    store[label] = entry
    store_path.write_text(json.dumps(store, indent=2))
    return Baseline(**entry)


def load_baseline(label: str, store_path: Path) -> Baseline:
    """Load a named baseline from the store."""
    if not store_path.exists():
        raise BaselineError(f"No baseline store found at {store_path}")
    try:
        store = json.loads(store_path.read_text())
    except json.JSONDecodeError as exc:
        raise BaselineError(f"Corrupt baseline store: {exc}") from exc
    if label not in store:
        raise BaselineError(f"Baseline '{label}' not found")
    return Baseline(**store[label])


def diff_against_baseline(
    label: str,
    current_env: Dict[str, str],
    store_path: Path,
    ignore: Optional[set] = None,
    check_values: bool = True,
) -> DiffResult:
    """Compare current env against a saved baseline."""
    baseline = load_baseline(label, store_path)
    return compare_envs(baseline.env, current_env, ignore=ignore or set(), check_values=check_values)


def list_baselines(store_path: Path) -> list[str]:
    """Return all stored baseline labels."""
    if not store_path.exists():
        return []
    try:
        store = json.loads(store_path.read_text())
    except json.JSONDecodeError:
        return []
    return list(store.keys())
