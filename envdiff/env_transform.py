"""Apply simple key/value transformations to an env mapping."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class TransformRule:
    key_pattern: str          # exact key or '*' wildcard suffix, e.g. '*_URL'
    operation: str            # 'uppercase', 'lowercase', 'strip', 'prefix', 'suffix', 'replace'
    argument: Optional[str] = None  # extra arg for prefix/suffix/replace


@dataclass
class TransformResult:
    original: Dict[str, str]
    transformed: Dict[str, str]
    changes: List[str] = field(default_factory=list)


def has_changes(result: TransformResult) -> bool:
    return bool(result.changes)


def _matches(key: str, pattern: str) -> bool:
    if pattern == "*":
        return True
    if pattern.startswith("*"):
        return key.endswith(pattern[1:])
    if pattern.endswith("*"):
        return key.startswith(pattern[:-1])
    return key == pattern


def _apply_op(value: str, op: str, arg: Optional[str]) -> str:
    if op == "uppercase":
        return value.upper()
    if op == "lowercase":
        return value.lower()
    if op == "strip":
        return value.strip()
    if op == "prefix" and arg is not None:
        return arg + value
    if op == "suffix" and arg is not None:
        return value + arg
    if op == "replace" and arg is not None:
        old, _, new = arg.partition(":")
        return value.replace(old, new)
    return value


def transform_env(
    env: Dict[str, str],
    rules: List[TransformRule],
) -> TransformResult:
    transformed = dict(env)
    changes: List[str] = []
    for key, value in env.items():
        for rule in rules:
            if _matches(key, rule.key_pattern):
                new_value = _apply_op(value, rule.operation, rule.argument)
                if new_value != value:
                    transformed[key] = new_value
                    changes.append(f"{key}: {value!r} -> {new_value!r}")
                break
    return TransformResult(original=env, transformed=transformed, changes=changes)
