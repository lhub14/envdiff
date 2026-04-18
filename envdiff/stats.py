"""Compute statistics across multiple .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.parser import parse_env_file


@dataclass
class EnvStats:
    file: str
    total_keys: int
    empty_values: int
    sensitive_keys: int
    unique_keys: List[str] = field(default_factory=list)
    shared_keys: List[str] = field(default_factory=list)


@dataclass
class StatsResult:
    files: List[EnvStats] = field(default_factory=list)
    all_keys: List[str] = field(default_factory=list)
    common_keys: List[str] = field(default_factory=list)


def _count_empty(env: Dict[str, str]) -> int:
    return sum(1 for v in env.values() if v == "")


def _count_sensitive(env: Dict[str, str]) -> int:
    from envdiff.redact import is_sensitive
    return sum(1 for k in env if is_sensitive(k))


def compute_stats(paths: List[str]) -> StatsResult:
    envs: Dict[str, Dict[str, str]] = {}
    for p in paths:
        envs[p] = parse_env_file(p)

    all_keys: set = set()
    for env in envs.values():
        all_keys.update(env.keys())

    common_keys: set = set(all_keys)
    for env in envs.values():
        common_keys &= set(env.keys())

    file_stats: List[EnvStats] = []
    for p, env in envs.items():
        keys = set(env.keys())
        file_stats.append(EnvStats(
            file=p,
            total_keys=len(env),
            empty_values=_count_empty(env),
            sensitive_keys=_count_sensitive(env),
            unique_keys=sorted(keys - common_keys),
            shared_keys=sorted(keys & common_keys),
        ))

    return StatsResult(
        files=file_stats,
        all_keys=sorted(all_keys),
        common_keys=sorted(common_keys),
    )
