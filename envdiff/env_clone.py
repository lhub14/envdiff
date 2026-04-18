"""Clone an env file to a new target, optionally filtering or redacting keys."""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file
from envdiff.redact import is_sensitive, redact_value
from envdiff.export import _to_dotenv


@dataclass
class CloneResult:
    source: str
    destination: str
    keys_written: List[str] = field(default_factory=list)
    keys_skipped: List[str] = field(default_factory=list)
    redacted_keys: List[str] = field(default_factory=list)


def has_skipped(result: CloneResult) -> bool:
    return bool(result.keys_skipped)


def clone_env(
    source: Path,
    destination: Path,
    *,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    redact: bool = False,
    dry_run: bool = False,
) -> CloneResult:
    """Clone *source* to *destination*, applying optional filters."""
    env = parse_env_file(source)
    result = CloneResult(source=str(source), destination=str(destination))

    filtered: Dict[str, str] = {}
    for key, value in env.items():
        if include is not None and key not in include:
            result.keys_skipped.append(key)
            continue
        if exclude is not None and key in exclude:
            result.keys_skipped.append(key)
            continue
        if redact and is_sensitive(key):
            filtered[key] = redact_value(value)
            result.redacted_keys.append(key)
        else:
            filtered[key] = value
        result.keys_written.append(key)

    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(_to_dotenv(filtered))

    return result
