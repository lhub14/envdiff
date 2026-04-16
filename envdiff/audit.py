"""Audit log: record diff results with timestamps for later review."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from envdiff.comparator import DiffResult


@dataclass
class AuditEntry:
    timestamp: str
    base: str
    target: str
    missing_in_target: List[str]
    missing_in_base: List[str]
    mismatched: List[str]
    has_diff: bool


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_entry(base_path: str, target_path: str, result: DiffResult) -> AuditEntry:
    return AuditEntry(
        timestamp=_now_iso(),
        base=base_path,
        target=target_path,
        missing_in_target=sorted(result.missing_in_target),
        missing_in_base=sorted(result.missing_in_base),
        mismatched=sorted(result.mismatched),
        has_diff=result.missing_in_target or result.missing_in_base or result.mismatched,
    )


def append_to_log(entry: AuditEntry, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry.__dict__) + "\n")


def load_log(log_path: Path) -> List[AuditEntry]:
    if not log_path.exists():
        return []
    entries: List[AuditEntry] = []
    with log_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                data = json.loads(line)
                entries.append(AuditEntry(**data))
    return entries
