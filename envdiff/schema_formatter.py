"""Format SchemaResult for terminal output."""
from __future__ import annotations

from envdiff.formatter import _red, _yellow, _green
from envdiff.schema import SchemaResult


def format_schema_result(result: SchemaResult, env_label: str = "env") -> str:
    lines: list[str] = []

    if not result.has_violations:
        lines.append(_green(f"✔ {env_label} matches schema — no violations found."))
        return "\n".join(lines)

    lines.append(_yellow(f"Schema violations for: {env_label}"))

    if result.missing_keys:
        lines.append(_red("  Missing keys (required by schema but absent in env):"))
        for key in result.missing_keys:
            lines.append(_red(f"    - {key}"))

    if result.extra_keys:
        lines.append(_yellow("  Extra keys (present in env but not in schema):"))
        for key in result.extra_keys:
            lines.append(_yellow(f"    + {key}"))

    return "\n".join(lines)
