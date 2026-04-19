"""Resolve variable interpolation in .env files (e.g. FOO=${BAR})."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolateResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved_keys: List[str] = field(default_factory=list)
    cycles: List[str] = field(default_factory=list)


def has_issues(result: InterpolateResult) -> bool:
    return bool(result.unresolved_keys or result.cycles)


def _refs(value: str) -> List[str]:
    return [m[0] or m[1] for m in _REF_RE.findall(value)]


def _resolve_value(key: str, env: Dict[str, str], cache: Dict[str, Optional[str]],
                   visiting: set) -> Optional[str]:
    if key in cache:
        return cache[key]
    if key not in env:
        return None
    raw = env[key]
    refs = _refs(raw)
    if not refs:
        cache[key] = raw
        return raw
    if key in visiting:
        return None  # cycle
    visiting.add(key)
    result = raw
    for ref in refs:
        resolved = _resolve_value(ref, env, cache, visiting)
        if resolved is None:
            visiting.discard(key)
            cache[key] = None
            return None
        result = result.replace("${" + ref + "}", resolved).replace("$" + ref, resolved)
    visiting.discard(key)
    cache[key] = result
    return result


def interpolate_env(env: Dict[str, str]) -> InterpolateResult:
    """Resolve all variable references in *env* and return an InterpolateResult."""
    cache: Dict[str, Optional[str]] = {}
    visiting: set = set()
    result = InterpolateResult()

    # Detect cycles first via DFS
    def _has_cycle(key: str, path: list) -> bool:
        if key in path:
            return True
        if key not in env:
            return False
        for ref in _refs(env[key]):
            if _has_cycle(ref, path + [key]):
                return True
        return False

    for key in env:
        if _has_cycle(key, []):
            result.cycles.append(key)

    for key in env:
        if key in result.cycles:
            result.resolved[key] = env[key]
            continue
        val = _resolve_value(key, env, cache, visiting)
        if val is None:
            result.unresolved_keys.append(key)
            result.resolved[key] = env[key]
        else:
            result.resolved[key] = val

    return result
