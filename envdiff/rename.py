"""Detect and suggest key renames between two env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Dict, List, Tuple


@dataclass
class RenameCandidate:
    old_key: str
    new_key: str
    score: float  # 0-1 similarity


@dataclass
class RenameResult:
    candidates: List[RenameCandidate] = field(default_factory=list)
    unmatched_base: List[str] = field(default_factory=list)
    unmatched_target: List[str] = field(default_factory=list)


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def detect_renames(
    base: Dict[str, str],
    target: Dict[str, str],
    threshold: float = 0.6,
) -> RenameResult:
    """Match keys missing from target against extra keys in target by name similarity."""
    base_keys = set(base)
    target_keys = set(target)

    missing_in_target = sorted(base_keys - target_keys)
    missing_in_base = sorted(target_keys - base_keys)

    candidates: List[RenameCandidate] = []
    used_new: set = set()

    for old in missing_in_target:
        best: Tuple[float, str] | None = None
        for new in missing_in_base:
            if new in used_new:
                continue
            score = _similarity(old, new)
            if score >= threshold and (best is None or score > best[0]):
                best = (score, new)
        if best:
            candidates.append(RenameCandidate(old_key=old, new_key=best[1], score=round(best[0], 3)))
            used_new.add(best[1])

    matched_old = {c.old_key for c in candidates}
    matched_new = {c.new_key for c in candidates}

    return RenameResult(
        candidates=candidates,
        unmatched_base=[k for k in missing_in_target if k not in matched_old],
        unmatched_target=[k for k in missing_in_base if k not in matched_new],
    )


def has_candidates(result: RenameResult) -> bool:
    return bool(result.candidates)
