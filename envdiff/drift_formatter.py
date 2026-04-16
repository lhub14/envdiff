"""Format DriftResult for terminal output."""
from envdiff.drift import DriftResult


def _red(t: str) -> str:
    return f"\033[31m{t}\033[0m"


def _green(t: str) -> str:
    return f"\033[32m{t}\033[0m"


def _yellow(t: str) -> str:
    return f"\033[33m{t}\033[0m"


def format_drift(result: DriftResult, *, color: bool = True) -> str:
    lines: list[str] = [f"Drift report for baseline label: {result.label}"]

    if not result.has_drift:
        msg = "No drift detected."
        lines.append(_green(msg) if color else msg)
        return "\n".join(lines)

    if result.added:
        lines.append("  Keys added (not in baseline):")
        for k in result.added:
            entry = f"    + {k}"
            lines.append(_green(entry) if color else entry)

    if result.removed:
        lines.append("  Keys removed (missing from current):")
        for k in result.removed:
            entry = f"    - {k}"
            lines.append(_red(entry) if color else entry)

    if result.changed:
        lines.append("  Keys with changed values:")
        for k in result.changed:
            entry = f"    ~ {k}"
            lines.append(_yellow(entry) if color else entry)

    return "\n".join(lines)
