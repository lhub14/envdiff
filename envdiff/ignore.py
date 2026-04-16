"""Support for .envdiffignore files — keys to skip during comparison."""

from __future__ import annotations

import re
from pathlib import Path


class IgnoreParseError(Exception):
    pass


def load_ignore_file(path: str | Path) -> set[str]:
    """Read an ignore file and return a set of key patterns to skip.

    Lines starting with '#' are comments. Blank lines are ignored.
    Patterns may use '*' as a wildcard.
    """
    p = Path(path)
    if not p.exists():
        return set()

    keys: set[str] = set()
    for lineno, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not re.match(r"^[A-Za-z0-9_*]+$", line):
            raise IgnoreParseError(
                f"Invalid pattern {line!r} on line {lineno} of {path}"
            )
        keys.add(line)
    return keys


def build_ignore_matcher(patterns: set[str]):
    """Return a callable that returns True if a key should be ignored."""
    regexes = [
        re.compile("^" + re.escape(p).replace(r"\*", ".*") + "$")
        for p in patterns
    ]

    def should_ignore(key: str) -> bool:
        return any(rx.match(key) for rx in regexes)

    return should_ignore
