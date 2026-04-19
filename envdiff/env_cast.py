"""Cast env values to typed Python objects with validation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


TYPE_CASTERS = {
    "int": int,
    "float": float,
    "bool": lambda v: v.lower() in ("1", "true", "yes", "on"),
    "str": str,
}


@dataclass
class CastIssue:
    key: str
    raw: str
    target_type: str
    reason: str


@dataclass
class CastResult:
    values: Dict[str, Any] = field(default_factory=dict)
    issues: List[CastIssue] = field(default_factory=list)


def has_issues(result: CastResult) -> bool:
    return bool(result.issues)


def cast_env(
    env: Dict[str, str],
    schema: Dict[str, str],
) -> CastResult:
    """Cast env values according to a type schema {KEY: type_name}.

    Unknown type names are treated as 'str'.
    Keys not in schema are passed through as strings.
    """
    result = CastResult()
    for key, raw in env.items():
        target = schema.get(key, "str")
        caster = TYPE_CASTERS.get(target, str)
        try:
            result.values[key] = caster(raw)
        except (ValueError, TypeError) as exc:
            result.issues.append(
                CastIssue(key=key, raw=raw, target_type=target, reason=str(exc))
            )
            result.values[key] = raw  # keep raw on failure
    return result


def cast_value(raw: str, target_type: str) -> Optional[Any]:
    """Cast a single value; returns None on failure."""
    caster = TYPE_CASTERS.get(target_type, str)
    try:
        return caster(raw)
    except (ValueError, TypeError):
        return None
