"""Formatter for FingerprintResult."""
from __future__ import annotations

from typing import Dict

from envdiff.env_diff_fingerprint import FingerprintResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def format_fingerprint_result(result: FingerprintResult, *, colour: bool = True) -> str:
    """Render a FingerprintResult as human-readable text."""
    lines: list[str] = []

    def c(fn, s: str) -> str:  # noqa: ANN001
        return fn(s) if colour else s

    lines.append(c(_bold, "Env File Fingerprints"))
    lines.append("")

    if not result.files:
        lines.append("  (no files)")
        return "\n".join(lines)

    for path, fp in sorted(result.files.items()):
        lines.append(f"  {c(_cyan, path):<40}  {fp}")

    if result.shape_groups:
        lines.append("")
        lines.append(c(_bold, "Shared Key Shapes"))
        for shape_hash, members in sorted(result.shape_groups.items()):
            lines.append(f"  shape:{c(_yellow, shape_hash)}")
            for m in members:
                lines.append(f"    - {m}")
    else:
        lines.append("")
        lines.append(c(_green, "No files share the same key shape."))

    return "\n".join(lines)
