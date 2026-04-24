"""Text formatter for HeatmapResult."""
from __future__ import annotations

from envdiff.env_diff_heatmap import HeatmapResult


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


_HEAT_COLOUR = {
    "cold": _green,
    "warm": _yellow,
    "hot": _red,
    "critical": _red,
}


def format_heatmap(result: HeatmapResult, *, colour: bool = True) -> str:
    if not result.rows:
        return "No differences recorded across comparisons."

    lines: list[str] = [
        f"Heatmap — {result.total_comparisons} comparison(s)\n",
        f"  {'KEY':<35} {'DIFFS':>6}  {'RATIO':>7}  HEAT",
        "  " + "-" * 60,
    ]
    for row in result.rows:
        heat_label = row.heat.upper()
        ratio_str = f"{row.ratio:.0%}"
        if colour:
            colourise = _HEAT_COLOUR.get(row.heat, str)
            heat_label = colourise(heat_label)
        lines.append(
            f"  {row.key:<35} {row.diff_count:>6}  {ratio_str:>7}  {heat_label}"
        )
    return "\n".join(lines)
