"""Summarise a collection of DiffResults into a compact statistics object."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class DiffSummary:
    total_files: int = 0
    files_with_diff: int = 0
    total_missing_in_target: int = 0
    total_missing_in_base: int = 0
    total_mismatched: int = 0
    per_file: Dict[str, dict] = field(default_factory=dict)

    @property
    def total_issues(self) -> int:
        return self.total_missing_in_target + self.total_missing_in_base + self.total_mismatched

    @property
    def clean(self) -> bool:
        return self.files_with_diff == 0


def summarise(results: Dict[str, DiffResult]) -> DiffSummary:
    """Build a DiffSummary from a mapping of label -> DiffResult."""
    summary = DiffSummary(total_files=len(results))

    for label, diff in results.items():
        missing_target = list(diff.missing_in_target)
        missing_base = list(diff.missing_in_base)
        mismatched = list(diff.mismatched.keys())

        file_issues = len(missing_target) + len(missing_base) + len(mismatched)
        if file_issues > 0:
            summary.files_with_diff += 1

        summary.total_missing_in_target += len(missing_target)
        summary.total_missing_in_base += len(missing_base)
        summary.total_mismatched += len(mismatched)

        summary.per_file[label] = {
            "missing_in_target": missing_target,
            "missing_in_base": missing_base,
            "mismatched": mismatched,
            "issues": file_issues,
        }

    return summary


def format_summary(summary: DiffSummary) -> str:
    """Return a human-readable summary string."""
    lines: List[str] = []
    lines.append(f"Files compared : {summary.total_files}")
    lines.append(f"Files with diff: {summary.files_with_diff}")
    lines.append(f"Missing in target : {summary.total_missing_in_target}")
    lines.append(f"Missing in base   : {summary.total_missing_in_base}")
    lines.append(f"Mismatched values : {summary.total_mismatched}")
    if summary.clean:
        lines.append("Status: OK")
    else:
        lines.append(f"Status: {summary.total_issues} issue(s) found")
    return "\n".join(lines)
