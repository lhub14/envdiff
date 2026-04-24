"""Format AliasResult for terminal output."""
from __future__ import annotations

from envdiff.env_alias import AliasResult, has_aliases


def _yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"


def _dim(text: str) -> str:
    return f"\033[2m{text}\033[0m"


def _bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


def format_alias_result(result: AliasResult, *, no_colour: bool = False) -> str:
    """Return a human-readable string describing alias groups."""
    yellow = (lambda t: t) if no_colour else _yellow
    dim = (lambda t: t) if no_colour else _dim
    bold = (lambda t: t) if no_colour else _bold

    if not has_aliases(result):
        return f"No aliases detected ({result.checked} keys checked)."

    lines: list[str] = [
        bold(f"{len(result.groups)} alias group(s) found "
             f"({result.checked} keys checked):"),
        "",
    ]

    for group in result.groups:
        display_val = group.value[:60] + "…" if len(group.value) > 60 else group.value
        lines.append(yellow(f'  value: "{display_val}"'))
        for filename, key in group.keys:
            lines.append(f"    {dim(filename)} → {key}")
        lines.append("")

    return "\n".join(lines).rstrip()
