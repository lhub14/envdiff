"""Format TrendResult for terminal output."""
from __future__ import annotations

from envdiff.env_diff_trend import TrendResult, is_improving, is_degrading


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def format_trend_result(result: TrendResult, *, colour: bool = True) -> str:
    if not result.points:
        return "No trend data available."

    lines: list[str] = [_bold("Diff Trend") if colour else "Diff Trend", ""]
    header = f"  {'Label':<20} {'Missing↓':>10} {'Missing↑':>10} {'Mismatch':>10} {'Total':>8}"
    lines.append(header)
    lines.append("  " + "-" * 62)

    for pt in result.points:
        total_str = str(pt.total_issues)
        if colour:
            if pt.total_issues == 0:
                total_str = _green(total_str)
            elif pt.total_issues <= 3:
                total_str = _yellow(total_str)
            else:
                total_str = _red(total_str)
        row = (
            f"  {pt.label:<20}"
            f" {pt.missing_in_target:>10}"
            f" {pt.missing_in_base:>10}"
            f" {pt.mismatched:>10}"
            f" {total_str:>8}"
        )
        lines.append(row)

    lines.append("")
    if len(result.points) >= 2:
        if is_improving(result):
            arrow = _green("↓ improving") if colour else "↓ improving"
        elif is_degrading(result):
            arrow = _red("↑ degrading") if colour else "↑ degrading"
        else:
            arrow = _yellow("→ stable") if colour else "→ stable"
        lines.append(f"  Trend: {arrow}")

    return "\n".join(lines)
