"""Compute a stable digest (hash) for an env file or a diff result.

Useful for detecting whether an env has changed between runs without
storing the full content.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, Optional

from envdiff.comparator import DiffResult


@dataclass
class DigestResult:
    base_digest: str
    target_digest: Optional[str]
    diff_digest: str
    changed: bool


def _stable_hash(data: str) -> str:
    """Return a short SHA-256 hex digest of *data*."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def digest_env(env: Dict[str, str]) -> str:
    """Return a deterministic digest for an env mapping."""
    serialised = json.dumps(env, sort_keys=True, separators=(",", ":"))
    return _stable_hash(serialised)


def digest_diff(diff: DiffResult) -> str:
    """Return a deterministic digest that captures the diff state."""
    payload = {
        "missing_in_target": sorted(diff.missing_in_target),
        "missing_in_base": sorted(diff.missing_in_base),
        "mismatched": {
            k: {"base": v[0], "target": v[1]}
            for k, v in sorted(diff.mismatched.items())
        },
    }
    serialised = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return _stable_hash(serialised)


def compute_digest(
    base_env: Dict[str, str],
    diff: DiffResult,
    target_env: Optional[Dict[str, str]] = None,
    previous_diff_digest: Optional[str] = None,
) -> DigestResult:
    """Compute digests for *base_env*, optional *target_env*, and *diff*.

    If *previous_diff_digest* is provided, ``changed`` reflects whether
    the diff has evolved since the last recorded digest.
    """
    base_digest = digest_env(base_env)
    target_digest = digest_env(target_env) if target_env is not None else None
    diff_digest = digest_diff(diff)
    changed = previous_diff_digest is None or diff_digest != previous_diff_digest
    return DigestResult(
        base_digest=base_digest,
        target_digest=target_digest,
        diff_digest=diff_digest,
        changed=changed,
    )
