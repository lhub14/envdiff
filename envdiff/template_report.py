"""Build structured reports from template generation."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TemplateReport:
    source: str
    total_keys: int
    redacted_keys: list[str] = field(default_factory=list)
    included_keys: list[str] = field(default_factory=list)


def build_template_report(
    source: str,
    env: dict[str, str],
    include_values: bool = False,
) -> TemplateReport:
    from envdiff.redact import is_sensitive

    redacted: list[str] = []
    included: list[str] = []
    for key in sorted(env):
        if include_values and not is_sensitive(key):
            included.append(key)
        else:
            redacted.append(key)
    return TemplateReport(
        source=source,
        total_keys=len(env),
        redacted_keys=redacted,
        included_keys=included,
    )


def template_report_to_json(report: TemplateReport) -> str:
    data: dict[str, Any] = {
        "source": report.source,
        "total_keys": report.total_keys,
        "redacted_keys": report.redacted_keys,
        "included_keys": report.included_keys,
    }
    return json.dumps(data, indent=2)


def template_report_to_text(report: TemplateReport) -> str:
    lines = [
        f"Source : {report.source}",
        f"Total  : {report.total_keys}",
        f"Redacted ({len(report.redacted_keys)}): {', '.join(report.redacted_keys) or 'none'}",
        f"Included ({len(report.included_keys)}): {', '.join(report.included_keys) or 'none'}",
    ]
    return "\n".join(lines)
