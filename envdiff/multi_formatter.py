"""Format MultiDiffResult for terminal output."""
from __future__ import annotations

from envdiff.comparator import has_differences
from envdiff.formatter import format_diff, _yellow, _green
from envdiff.multi import MultiDiffResult


def format_multi_diff(result: MultiDiffResult, *, color: bool = True) -> str:
    """Return a human-readable string for a multi-file comparison."""
    lines: list[str] = []
    header = f"Base: {result.base}"
    lines.append(header)
    lines.append("=" * len(header))

    for target, diff in result.results.items():
        section = f"\n--- {target} ---"
        lines.append(_yellow(section) if color else section)
        if not has_differences(diff):
            msg = "  No differences."
            lines.append(_green(msg) if color else msg)
        else:
            lines.append(format_diff(diff, color=color).rstrip())

    return "\n".join(lines)
