"""Lint .env files for common issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import re


@dataclass
class LintIssue:
    line: int
    key: str | None
    message: str
    severity: str  # "error" | "warning"


@dataclass
class LintResult:
    path: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_issues(self) -> bool:
        return bool(self.issues)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


_VALID_KEY = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
_UPPER_KEY = re.compile(r'^[A-Z_][A-Z0-9_]*$')


def lint_env_file(path: str) -> LintResult:
    result = LintResult(path=path)
    try:
        lines = open(path).readlines()
    except OSError as exc:
        result.issues.append(LintIssue(line=0, key=None, message=str(exc), severity="error"))
        return result

    seen: dict[str, int] = {}
    for lineno, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in line:
            result.issues.append(LintIssue(lineno, None, f"No '=' found: {line!r}", "error"))
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not _VALID_KEY.match(key):
            result.issues.append(LintIssue(lineno, key, f"Invalid key name: {key!r}", "error"))
        elif not _UPPER_KEY.match(key):
            result.issues.append(LintIssue(lineno, key, f"Key not UPPER_SNAKE_CASE: {key!r}", "warning"))
        if key in seen:
            result.issues.append(LintIssue(lineno, key, f"Duplicate key (first at line {seen[key]})", "warning"))
        else:
            seen[key] = lineno
        if value.strip() == "" :
            result.issues.append(LintIssue(lineno, key, f"Empty value for key {key!r}", "warning"))
    return result
