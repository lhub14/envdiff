"""Suggest default values for missing keys based on key name heuristics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_HEURISTICS: List[tuple] = [
    (("PORT", "_PORT"), "8080"),
    (("HOST", "_HOST"), "localhost"),
    (("DEBUG",), "false"),
    (("LOG_LEVEL", "LOGLEVEL"), "info"),
    (("ENV", "ENVIRONMENT", "APP_ENV"), "development"),
    (("TIMEOUT",), "30"),
    (("MAX_RETRIES",), "3"),
    (("DB_PORT", "DATABASE_PORT"), "5432"),
    (("REDIS_PORT",), "6379"),
    (("TZ", "TIMEZONE"), "UTC"),
]


@dataclass
class Suggestion:
    key: str
    value: str
    reason: str


@dataclass
class SuggestResult:
    suggestions: List[Suggestion] = field(default_factory=list)
    unmatched: List[str] = field(default_factory=list)


def _suggest_for_key(key: str) -> Optional[str]:
    upper = key.upper()
    for patterns, value in _HEURISTICS:
        for pat in patterns:
            if upper == pat or upper.endswith(pat):
                return value
    return None


def suggest_defaults(missing_keys: List[str]) -> SuggestResult:
    """Return suggested default values for a list of missing keys."""
    suggestions: List[Suggestion] = []
    unmatched: List[str] = []
    for key in missing_keys:
        val = _suggest_for_key(key)
        if val is not None:
            suggestions.append(Suggestion(key=key, value=val, reason="heuristic match"))
        else:
            unmatched.append(key)
    return SuggestResult(suggestions=suggestions, unmatched=unmatched)
