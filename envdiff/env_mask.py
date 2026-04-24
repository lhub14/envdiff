"""Mask sensitive values in an env dict for safe display or logging."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.redact import is_sensitive

_DEFAULT_MASK = "***"
_DEFAULT_REVEAL_CHARS = 0


@dataclass
class MaskResult:
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)


def has_masked(result: MaskResult) -> bool:
    return len(result.masked_keys) > 0


def _mask_value(value: str, mask: str, reveal_chars: int) -> str:
    """Return a masked version of *value*.

    If *reveal_chars* > 0 the last N characters of the value are kept so that
    users can distinguish between different secrets.
    """
    if not value:
        return value
    if reveal_chars <= 0 or reveal_chars >= len(value):
        return mask
    suffix = value[-reveal_chars:]
    return f"{mask}{suffix}"


def mask_env(
    env: Dict[str, str],
    *,
    extra_keys: List[str] | None = None,
    mask: str = _DEFAULT_MASK,
    reveal_chars: int = _DEFAULT_REVEAL_CHARS,
) -> MaskResult:
    """Return a *MaskResult* with sensitive values replaced by *mask*.

    Parameters
    ----------
    env:
        Parsed environment dict.
    extra_keys:
        Additional key names that should always be masked regardless of the
        default sensitivity heuristic.
    mask:
        Replacement string (default ``"***"``).
    reveal_chars:
        Number of trailing characters to preserve so secrets can be told
        apart.  0 means full replacement.
    """
    extra = {k.upper() for k in (extra_keys or [])}
    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for key, value in env.items():
        if is_sensitive(key) or key.upper() in extra:
            masked[key] = _mask_value(value, mask, reveal_chars)
            masked_keys.append(key)
        else:
            masked[key] = value

    return MaskResult(original=dict(env), masked=masked, masked_keys=sorted(masked_keys))
