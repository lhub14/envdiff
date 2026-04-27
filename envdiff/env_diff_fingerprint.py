"""Fingerprint-based env file identity tracking.

Computes a stable fingerprint for each env file and detects
whether two files share the same structural shape (same keys,
regardless of values).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FingerprintResult:
    files: Dict[str, str] = field(default_factory=dict)  # path -> fingerprint
    shape_groups: Dict[str, List[str]] = field(default_factory=dict)  # shape_hash -> [paths]


def _key_fingerprint(env: Dict[str, str]) -> str:
    """Hash of sorted key names only (shape fingerprint)."""
    key_blob = "\n".join(sorted(env.keys()))
    return hashlib.sha1(key_blob.encode()).hexdigest()[:12]


def _value_fingerprint(env: Dict[str, str]) -> str:
    """Hash of sorted key=value pairs (full fingerprint)."""
    pair_blob = "\n".join(f"{k}={v}" for k, v in sorted(env.items()))
    return hashlib.sha1(pair_blob.encode()).hexdigest()[:12]


def compute_fingerprints(envs: Dict[str, Dict[str, str]]) -> FingerprintResult:
    """Compute full and shape fingerprints for each named env file.

    Args:
        envs: Mapping of file path (or label) to parsed env dict.

    Returns:
        FingerprintResult with per-file fingerprints and shape groups.
    """
    result = FingerprintResult()
    shape_map: Dict[str, List[str]] = {}

    for path, env in envs.items():
        fp = _value_fingerprint(env)
        shape = _key_fingerprint(env)
        result.files[path] = fp
        shape_map.setdefault(shape, []).append(path)

    # Only record groups with more than one member (shared shapes)
    result.shape_groups = {k: v for k, v in shape_map.items() if len(v) > 1}
    return result


def identical(result: FingerprintResult, a: str, b: str) -> bool:
    """Return True if files *a* and *b* have the same full fingerprint."""
    return result.files.get(a) == result.files.get(b)


def same_shape(result: FingerprintResult, a: str, b: str) -> bool:
    """Return True if files *a* and *b* share the same set of keys."""
    for members in result.shape_groups.values():
        if a in members and b in members:
            return True
    return False
