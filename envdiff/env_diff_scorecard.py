"""Per-key scorecard: aggregates diff, lint, and schema signals into a per-key table."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult
from envdiff.lint import LintResult
from envdiff.schema import SchemaResult


@dataclass
class ScorecardRow:
    key: str
    in_base: bool
    in_target: bool
    values_match: bool
    lint_warnings: List[str] = field(default_factory=list)
    schema_violations: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return (
            self.in_base
            and self.in_target
            and self.values_match
            and not self.lint_warnings
            and not self.schema_violations
        )


@dataclass
class ScorecardResult:
    rows: List[ScorecardRow] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.rows)

    @property
    def passing(self) -> int:
        return sum(1 for r in self.rows if r.ok)

    @property
    def failing(self) -> int:
        return self.total - self.passing


def build_scorecard(
    diff: DiffResult,
    lint: Optional[LintResult] = None,
    schema: Optional[SchemaResult] = None,
) -> ScorecardResult:
    """Combine diff, lint, and schema results into a per-key scorecard."""
    all_keys: set = set()
    all_keys.update(diff.missing_in_target)
    all_keys.update(diff.missing_in_base)
    all_keys.update(diff.mismatched.keys())
    # keys that are fine in the diff
    if hasattr(diff, "base") and diff.base:
        all_keys.update(diff.base.keys())

    lint_warn_map: Dict[str, List[str]] = {}
    if lint:
        for issue in lint.issues:
            lint_warn_map.setdefault(issue.key, []).append(issue.message)

    schema_viol_map: Dict[str, List[str]] = {}
    if schema:
        for key in schema.missing_required:
            schema_viol_map.setdefault(key, []).append("missing required key")
        for key, pattern in schema.invalid_pattern.items():
            schema_viol_map.setdefault(key, []).append(f"pattern mismatch: {pattern}")

    rows: List[ScorecardRow] = []
    for key in sorted(all_keys):
        in_base = key not in diff.missing_in_base
        in_target = key not in diff.missing_in_target
        values_match = key not in diff.mismatched
        rows.append(
            ScorecardRow(
                key=key,
                in_base=in_base,
                in_target=in_target,
                values_match=values_match,
                lint_warnings=lint_warn_map.get(key, []),
                schema_violations=schema_viol_map.get(key, []),
            )
        )
    return ScorecardResult(rows=rows)
