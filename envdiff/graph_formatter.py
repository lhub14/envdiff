"""Human-readable formatting for GraphResult."""
from __future__ import annotations

from envdiff.graph import GraphResult


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def format_graph(result: GraphResult, no_color: bool = False) -> str:
    lines: list[str] = []

    def b(s: str) -> str:
        return s if no_color else _bold(s)

    def c(s: str) -> str:
        return s if no_color else _cyan(s)

    def y(s: str) -> str:
        return s if no_color else _yellow(s)

    def d(s: str) -> str:
        return s if no_color else _dim(s)

    lines.append(b("Key Presence Graph"))
    lines.append("")

    lines.append(b(f"Universal ({len(result.universal)} keys) — present in all files:"))
    for key in sorted(result.universal):
        lines.append(f"  {c(key)}")
    if not result.universal:
        lines.append(d("  (none)"))

    lines.append("")
    lines.append(b(f"Partial ({len(result.partial)} keys) — present in some files:"))
    for key in sorted(result.partial):
        files = ", ".join(sorted(result.partial[key]))
        lines.append(f"  {y(key)}  {d(f'[{files}]')}")
    if not result.partial:
        lines.append(d("  (none)"))

    lines.append("")
    lines.append(b(f"Unique ({len(result.unique)} keys) — present in exactly one file:"))
    for key in sorted(result.unique):
        lines.append(f"  {key}  {d(f'[{result.unique[key]}]')}")
    if not result.unique:
        lines.append(d("  (none)"))

    return "\n".join(lines)
