"""Validate .env values against simple type/format rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Built-in rule patterns
_RULES: Dict[str, str] = {
    "int": r"^-?\d+$",
    "bool": r"^(true|false|1|0|yes|no)$",
    "url": r"^https?://.+",
    "email": r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    "nonempty": r".+",
}


@dataclass
class ValidationIssue:
    key: str
    value: str
    rule: str
    message: str


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.issues) == 0


def _resolve_pattern(rule: str) -> Optional[str]:
    """Return regex for a named rule or treat rule itself as a regex."""
    return _RULES.get(rule, rule)


def validate_env(
    env: Dict[str, str],
    rules: Dict[str, str],
    *,
    case_insensitive: bool = True,
) -> ValidationResult:
    """Validate *env* against *rules* mapping key -> rule name or regex.

    Args:
        env: Parsed environment dict.
        rules: Mapping of env key to rule name (e.g. "int") or raw regex.
        case_insensitive: Whether bool/flag patterns match case-insensitively.

    Returns:
        ValidationResult with any issues found.
    """
    result = ValidationResult()
    flags = re.IGNORECASE if case_insensitive else 0

    for key, rule in rules.items():
        if key not in env:
            continue  # missing keys are handled by comparator
        value = env[key]
        pattern = _resolve_pattern(rule)
        if not re.search(pattern, value, flags):
            result.issues.append(
                ValidationIssue(
                    key=key,
                    value=value,
                    rule=rule,
                    message=f"{key}={value!r} does not match rule '{rule}'",
                )
            )
    return result
