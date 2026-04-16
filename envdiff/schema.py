"""Schema validation: check that env keys match an expected set."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class SchemaParseError(Exception):
    pass


@dataclass
class SchemaResult:
    extra_keys: list[str] = field(default_factory=list)
    missing_keys: list[str] = field(default_factory=list)

    @property
    def has_violations(self) -> bool:
        return bool(self.extra_keys or self.missing_keys)


def load_schema(path: Path) -> set[str]:
    """Load a schema file — one key name per line, comments with # allowed."""
    if not path.exists():
        raise SchemaParseError(f"Schema file not found: {path}")
    keys: set[str] = set()
    for lineno, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not line.isidentifier() and not all(c.isalnum() or c == "_" for c in line):
            raise SchemaParseError(f"Invalid key '{line}' at line {lineno}")
        keys.add(line)
    return keys


def validate_against_schema(
    env_keys: set[str],
    schema_keys: set[str],
) -> SchemaResult:
    """Return keys missing from env and keys present in env but not in schema."""
    missing = sorted(schema_keys - env_keys)
    extra = sorted(env_keys - schema_keys)
    return SchemaResult(extra_keys=extra, missing_keys=missing)
