"""Build text/JSON reports for encrypted env file operations."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EncryptReport:
    operation: str  # 'lock' or 'unlock'
    source: str
    destination: str
    keys_processed: List[str] = field(default_factory=list)
    success: bool = True
    error: str | None = None


def build_encrypt_report(
    operation: str,
    source: str,
    destination: str,
    env: Dict[str, str],
    error: str | None = None,
) -> EncryptReport:
    return EncryptReport(
        operation=operation,
        source=source,
        destination=destination,
        keys_processed=sorted(env.keys()),
        success=error is None,
        error=error,
    )


def encrypt_report_to_json(report: EncryptReport) -> str:
    return json.dumps(
        {
            "operation": report.operation,
            "source": report.source,
            "destination": report.destination,
            "keys_processed": report.keys_processed,
            "key_count": len(report.keys_processed),
            "success": report.success,
            "error": report.error,
        },
        indent=2,
    )


def encrypt_report_to_text(report: EncryptReport) -> str:
    lines: List[str] = []
    status = "OK" if report.success else "FAILED"
    lines.append(f"Operation : {report.operation}")
    lines.append(f"Source    : {report.source}")
    lines.append(f"Destination: {report.destination}")
    lines.append(f"Status    : {status}")
    if report.error:
        lines.append(f"Error     : {report.error}")
    else:
        lines.append(f"Keys      : {len(report.keys_processed)}")
        for k in report.keys_processed:
            lines.append(f"  - {k}")
    return "\n".join(lines)
