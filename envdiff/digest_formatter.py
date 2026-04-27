"""Format a DigestResult for human-readable or JSON output."""
from __future__ import annotations

import json
from typing import Optional

from envdiff.env_diff_digest import DigestResult


def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


def _green(text: str) -> str:
    return f"\033[32m{text}\033[0m"


def _yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"


def format_digest_result(
    result: DigestResult,
    *,
    colour: bool = True,
    label_base: str = "base",
    label_target: Optional[str] = "target",
) -> str:
    """Return a formatted string summarising the digest result."""
    lines: list[str] = []

    def _maybe(text: str, colour_fn) -> str:  # type: ignore[type-arg]
        return colour_fn(text) if colour else text

    lines.append(_maybe(f"{label_base} digest : {result.base_digest}", _bold))
    if result.target_digest is not None and label_target:
        lines.append(_maybe(f"{label_target} digest : {result.target_digest}", _bold))
    lines.append(_maybe(f"diff digest    : {result.diff_digest}", _bold))

    status = "changed" if result.changed else "unchanged"
    colour_fn = _yellow if result.changed else _green
    lines.append(_maybe(f"status         : {status}", colour_fn))
    return "\n".join(lines)


def digest_result_to_json(result: DigestResult) -> str:
    """Serialise *result* to a JSON string."""
    return json.dumps(
        {
            "base_digest": result.base_digest,
            "target_digest": result.target_digest,
            "diff_digest": result.diff_digest,
            "changed": result.changed,
        },
        indent=2,
    )
