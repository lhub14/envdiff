"""Generate structured reports from diff results."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Literal

from envdiff.comparator import DiffResult


ReportFormat = Literal["text", "json", "markdown"]


@dataclass
class Report:
    format: ReportFormat
    content: str
    has_differences: bool


def _to_json(base_name: str, target_name: str, diff: DiffResult) -> str:
    data = {
        "base": base_name,
        "target": target_name,
        "missing_in_target": list(diff.missing_in_target),
        "missing_in_base": list(diff.missing_in_base),
        "mismatched": [
            {"key": k, "base": v[0], "target": v[1]}
            for k, v in diff.mismatched.items()
        ],
    }
    return json.dumps(data, indent=2)


def _to_markdown(base_name: str, target_name: str, diff: DiffResult) -> str:
    lines = [f"# Env Diff: `{base_name}` vs `{target_name}`", ""]
    if diff.missing_in_target:
        lines.append(f"## Missing in `{target_name}`")
        for k in sorted(diff.missing_in_target):
            lines.append(f"- `{k}`")
        lines.append("")
    if diff.missing_in_base:
        lines.append(f"## Missing in `{base_name}`")
        for k in sorted(diff.missing_in_base):
            lines.append(f"- `{k}`")
        lines.append("")
    if diff.mismatched:
        lines.append("## Mismatched Values")
        for k, (bv, tv) in sorted(diff.mismatched.items()):
            lines.append(f"- `{k}`: `{bv}` → `{tv}`")
        lines.append("")
    if not (diff.missing_in_target or diff.missing_in_base or diff.mismatched):
        lines.append("_No differences found._")
    return "\n".join(lines)


def generate_report(
    base_name: str,
    target_name: str,
    diff: DiffResult,
    fmt: ReportFormat = "text",
) -> Report:
    from envdiff.formatter import format_diff
    from envdiff.comparator import has_differences

    if fmt == "json":
        content = _to_json(base_name, target_name, diff)
    elif fmt == "markdown":
        content = _to_markdown(base_name, target_name, diff)
    else:
        content = format_diff(base_name, target_name, diff)

    return Report(format=fmt, content=content, has_differences=has_differences(diff))
