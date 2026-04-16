"""Format audit log entries for terminal display."""
from __future__ import annotations

from typing import List

from envdiff.audit import AuditEntry


def _status(entry: AuditEntry) -> str:
    return "DIFF" if entry.has_diff else "OK"


def format_audit_log(entries: List[AuditEntry]) -> str:
    if not entries:
        return "No audit entries found."
    lines: List[str] = []
    for e in entries:
        lines.append(f"[{e.timestamp}] {_status(e)}  {e.base} vs {e.target}")
        if e.missing_in_target:
            lines.append(f"  missing in target : {', '.join(e.missing_in_target)}")
        if e.missing_in_base:
            lines.append(f"  missing in base   : {', '.join(e.missing_in_base)}")
        if e.mismatched:
            lines.append(f"  mismatched        : {', '.join(e.mismatched)}")
    return "\n".join(lines)
