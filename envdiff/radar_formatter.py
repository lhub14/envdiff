"""Text formatter for RadarResult."""
from __future__ import annotations

from envdiff.env_diff_radar import RadarResult, RadarEntry


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _bar(value: float, width: int = 20) -> str:
    filled = round(value * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def _colour_value(v: float) -> str:
    pct = f"{v * 100:.1f}%"
    if v >= 0.9:
        return _green(pct)
    if v >= 0.6:
        return _yellow(pct)
    return _red(pct)


def _format_entry(entry: RadarEntry) -> str:
    lines = [_bold(f"  {entry.label}")]
    for axis in entry.axes:
        bar = _bar(axis.value)
        lines.append(
            f"    {axis.name:<14} {bar}  {_colour_value(axis.value)}"
        )
    lines.append(f"    {'overall':<14}              {_colour_value(entry.score())}")
    return "\n".join(lines)


def format_radar_result(result: RadarResult, *, colour: bool = True) -> str:
    if not result.entries:
        return "No targets to compare."
    header = _bold(f"Radar — base: {result.base_label}") if colour else f"Radar — base: {result.base_label}"
    parts = [header]
    for entry in result.entries:
        parts.append(_format_entry(entry) if colour else _format_entry(entry))
    return "\n".join(parts)
