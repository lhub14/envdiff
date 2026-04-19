"""Format CastResult for terminal output."""
from __future__ import annotations

from envdiff.env_cast import CastResult, has_issues


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_cast_result(result: CastResult, *, colour: bool = True) -> str:
    lines: list[str] = []

    if not has_issues(result):
        msg = "All values cast successfully."
        lines.append(_green(msg) if colour else msg)
    else:
        header = f"{len(result.issues)} cast issue(s) found:"
        lines.append(_red(header) if colour else header)
        for issue in result.issues:
            detail = (
                f"  {issue.key}: cannot cast {issue.raw!r} "
                f"to {issue.target_type} — {issue.reason}"
            )
            lines.append(_red(detail) if colour else detail)

    if result.values:
        lines.append("")
        lines.append("Typed values:")
        for k, v in sorted(result.values.items()):
            type_label = _dim(f"({type(v).__name__})") if colour else f"({type(v).__name__})"
            lines.append(f"  {k}={v!r} {type_label}")

    return "\n".join(lines)
