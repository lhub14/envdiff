"""Generate structured reports for schema validation results."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

from .schema import SchemaResult


@dataclass
class SchemaReport:
    env_file: str
    schema_file: str
    missing_required: List[str]
    invalid_pattern: List[str]
    total_violations: int


def build_schema_report(env_file: str, schema_file: str, result: SchemaResult) -> SchemaReport:
    total = len(result.missing_required) + len(result.invalid_pattern)
    return SchemaReport(
        env_file=env_file,
        schema_file=schema_file,
        missing_required=sorted(result.missing_required),
        invalid_pattern=sorted(result.invalid_pattern),
        total_violations=total,
    )


def schema_report_to_json(report: SchemaReport) -> str:
    return json.dumps(
        {
            "env_file": report.env_file,
            "schema_file": report.schema_file,
            "missing_required": report.missing_required,
            "invalid_pattern": report.invalid_pattern,
            "total_violations": report.total_violations,
        },
        indent=2,
    )


def schema_report_to_markdown(report: SchemaReport) -> str:
    lines = [f"# Schema Validation Report", f"", f"- **Env file**: `{report.env_file}`",
             f"- **Schema file**: `{report.schema_file}`", ""]
    if report.missing_required:
        lines += ["## Missing Required Keys", ""]
        lines += [f"- `{k}`" for k in report.missing_required]
        lines.append("")
    if report.invalid_pattern:
        lines += ["## Invalid Pattern Keys", ""]
        lines += [f"- `{k}`" for k in report.invalid_pattern]
        lines.append("")
    if not report.missing_required and not report.invalid_pattern:
        lines.append("_No violations found._")
    return "\n".join(lines)
