"""Filter DiffResult entries by key patterns or diff type."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Iterable

from envdiff.comparator import DiffResult


@dataclass
class FilterOptions:
    include_patterns: list[str] = field(default_factory=list)  # glob patterns
    exclude_patterns: list[str] = field(default_factory=list)
    only_missing: bool = False   # only keys missing in target
    only_extra: bool = False     # only keys missing in base
    only_mismatch: bool = False  # only value mismatches


def _matches_any(key: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(key, p) for p in patterns)


def filter_diff(result: DiffResult, opts: FilterOptions) -> DiffResult:
    """Return a new DiffResult with entries filtered according to opts."""

    def _keep_key(key: str, bucket: str) -> bool:
        if opts.include_patterns and not _matches_any(key, opts.include_patterns):
            return False
        if opts.exclude_patterns and _matches_any(key, opts.exclude_patterns):
            return False
        if opts.only_missing and bucket != "missing_in_target":
            return False
        if opts.only_extra and bucket != "missing_in_base":
            return False
        if opts.only_mismatch and bucket != "mismatched":
            return False
        return True

    missing_in_target = [
        k for k in result.missing_in_target if _keep_key(k, "missing_in_target")
    ]
    missing_in_base = [
        k for k in result.missing_in_base if _keep_key(k, "missing_in_base")
    ]
    mismatched = {
        k: v
        for k, v in result.mismatched.items()
        if _keep_key(k, "mismatched")
    }

    return DiffResult(
        missing_in_target=missing_in_target,
        missing_in_base=missing_in_base,
        mismatched=mismatched,
    )
