"""Split a .env file into multiple files by key prefix."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

from envdiff.parser import parse_env_file


@dataclass
class SplitResult:
    groups: Dict[str, Dict[str, str]] = field(default_factory=dict)
    unmatched: Dict[str, str] = field(default_factory=dict)


def has_unmatched(result: SplitResult) -> bool:
    return bool(result.unmatched)


def split_by_prefix(
    env: Dict[str, str],
    prefixes: List[str],
    strip_prefix: bool = False,
) -> SplitResult:
    """Partition *env* into groups based on key prefixes.

    Keys that match no prefix land in ``unmatched``.
    """
    result = SplitResult()
    for prefix in prefixes:
        result.groups[prefix] = {}

    for key, value in env.items():
        matched = False
        for prefix in prefixes:
            if key.startswith(prefix):
                out_key = key[len(prefix):] if strip_prefix else key
                result.groups[prefix][out_key] = value
                matched = True
                break
        if not matched:
            result.unmatched[key] = value

    return result


def split_env_file(
    path: Path,
    prefixes: List[str],
    strip_prefix: bool = False,
) -> SplitResult:
    env = parse_env_file(path)
    return split_by_prefix(env, prefixes, strip_prefix=strip_prefix)


def write_split_files(
    result: SplitResult,
    output_dir: Path,
    suffix: str = ".env",
) -> List[Path]:
    """Write each group to *output_dir/<prefix><suffix>*.

    Returns list of paths written.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for prefix, env in result.groups.items():
        safe = re.sub(r"[^\w.-]", "_", prefix).strip("_").lower()
        dest = output_dir / f"{safe}{suffix}"
        lines = [f"{k}={v}\n" for k, v in sorted(env.items())]
        dest.write_text("".join(lines))
        written.append(dest)
    return written
