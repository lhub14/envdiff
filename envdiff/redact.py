"""Redaction helpers for sensitive env values."""

import re
from typing import Dict

_SENSITIVE_PATTERNS = [
    re.compile(r"(password|passwd|secret|token|api_key|apikey|auth|credential|private_key|access_key)", re.IGNORECASE),
]

REDACTED = "***REDACTED***"


def is_sensitive(key: str) -> bool:
    """Return True if the key name looks sensitive."""
    for pattern in _SENSITIVE_PATTERNS:
        if pattern.search(key):
            return True
    return False


def redact_env(env: Dict[str, str], *, extra_keys: frozenset = frozenset()) -> Dict[str, str]:
    """Return a copy of env with sensitive values replaced by REDACTED."""
    result: Dict[str, str] = {}
    for key, value in env.items():
        if is_sensitive(key) or key in extra_keys:
            result[key] = REDACTED
        else:
            result[key] = value
    return result


def redact_value(key: str, value: str, *, extra_keys: frozenset = frozenset()) -> str:
    """Return REDACTED if key is sensitive, otherwise return value unchanged."""
    if is_sensitive(key) or key in extra_keys:
        return REDACTED
    return value
