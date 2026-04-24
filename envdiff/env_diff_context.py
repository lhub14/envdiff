"""Contextual diff: show surrounding keys around changed lines."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.comparator import DiffResult


@dataclass
class ContextBlock:
    """A changed key with its surrounding context lines."""
    key: str
    change_type: str  # 'missing_in_target' | 'missing_in_base' | 'mismatch'
    before: List[Tuple[str, str]] = field(default_factory=list)  # (key, value)
    after: List[Tuple[str, str]] = field(default_factory=list)   # (key, value)
    base_value: str | None = None
    target_value: str | None = None


@dataclass
class ContextDiffResult:
    blocks: List[ContextBlock] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.blocks) == 0


def build_context_diff(
    base: Dict[str, str],
    target: Dict[str, str],
    diff: DiffResult,
    context: int = 2,
) -> ContextDiffResult:
    """Attach surrounding key context to each diff entry."""
    ordered_keys = list(base.keys())
    # Include keys only in target so they appear in order too
    for k in target:
        if k not in base:
            ordered_keys.append(k)

    changed: set[str] = (
        set(diff.missing_in_target)
        | set(diff.missing_in_base)
        | set(diff.mismatched.keys())
    )

    def _change_type(key: str) -> str:
        if key in diff.missing_in_target:
            return "missing_in_target"
        if key in diff.missing_in_base:
            return "missing_in_base"
        return "mismatch"

    def _pair(k: str) -> Tuple[str, str]:
        val = base.get(k) or target.get(k, "")
        return (k, val)

    blocks: List[ContextBlock] = []
    for idx, key in enumerate(ordered_keys):
        if key not in changed:
            continue
        before_keys = [
            ordered_keys[i]
            for i in range(max(0, idx - context), idx)
            if ordered_keys[i] not in changed
        ]
        after_keys = [
            ordered_keys[i]
            for i in range(idx + 1, min(len(ordered_keys), idx + 1 + context))
            if ordered_keys[i] not in changed
        ]
        ct = _change_type(key)
        bv, tv = None, None
        if ct == "mismatch":
            bv, tv = diff.mismatched[key]
        elif ct == "missing_in_target":
            bv = base.get(key)
        else:
            tv = target.get(key)
        blocks.append(ContextBlock(
            key=key,
            change_type=ct,
            before=[_pair(k) for k in before_keys],
            after=[_pair(k) for k in after_keys],
            base_value=bv,
            target_value=tv,
        ))
    return ContextDiffResult(blocks=blocks)
