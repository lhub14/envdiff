"""Pin current env key set to a snapshot file for later comparison."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

PIN_VERSION = 1


class PinError(Exception):
    pass


def save_pin(keys: List[str], pin_file: Path) -> None:
    """Save a sorted list of key names to a JSON pin file."""
    pin_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": PIN_VERSION, "keys": sorted(set(keys))}
    pin_file.write_text(json.dumps(payload, indent=2))


def load_pin(pin_file: Path) -> List[str]:
    """Load pinned keys from a JSON pin file."""
    if not pin_file.exists():
        raise PinError(f"Pin file not found: {pin_file}")
    try:
        payload = json.loads(pin_file.read_text())
    except json.JSONDecodeError as exc:
        raise PinError(f"Invalid pin file: {exc}") from exc
    if "keys" not in payload:
        raise PinError("Pin file missing 'keys' field")
    return list(payload["keys"])


def diff_against_pin(env: Dict[str, str], pin_file: Path) -> Dict[str, List[str]]:
    """Return keys added/removed compared to the pinned snapshot.

    Returns a dict with:
      'added'   – keys present in env but not in pin
      'removed' – keys in pin but missing from env
    """
    pinned = set(load_pin(pin_file))
    current = set(env.keys())
    return {
        "added": sorted(current - pinned),
        "removed": sorted(pinned - current),
    }


def is_clean(env: Dict[str, str], pin_file: Path) -> bool:
    result = diff_against_pin(env, pin_file)
    return not result["added"] and not result["removed"]
