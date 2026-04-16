"""Parser for .env files."""

from pathlib import Path
from typing import Dict, Optional


class EnvParseError(Exception):
    """Raised when a .env file cannot be parsed."""


def parse_env_file(filepath: str | Path) -> Dict[str, Optional[str]]:
    """Parse a .env file and return a dict of key-value pairs.

    Supports:
    - KEY=VALUE
    - KEY="VALUE" or KEY='VALUE'
    - Comments starting with #
    - Empty lines
    - Keys with no value (KEY=)

    Args:
        filepath: Path to the .env file.

    Returns:
        Dictionary mapping variable names to their values.

    Raises:
        EnvParseError: If the file cannot be read or contains invalid syntax.
    """
    path = Path(filepath)

    if not path.exists():
        raise EnvParseError(f"File not found: {filepath}")

    if not path.is_file():
        raise EnvParseError(f"Not a file: {filepath}")

    env: Dict[str, Optional[str]] = {}

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EnvParseError(f"Cannot read file {filepath}: {exc}") from exc

    for lineno, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()

        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            raise EnvParseError(
                f"Invalid syntax at {filepath}:{lineno} — missing '=': {raw_line!r}"
            )

        key, _, value = line.partition("=")
        key = key.strip()

        if not key:
            raise EnvParseError(
                f"Empty key at {filepath}:{lineno}: {raw_line!r}"
            )

        if not _is_valid_key(key):
            raise EnvParseError(
                f"Invalid key at {filepath}:{lineno} — keys must contain only "
                f"alphanumeric characters and underscores: {key!r}"
            )

        # Strip inline comments (only outside quotes)
        value = value.strip()
        if value and value[0] in ('"', "'"):
            quote = value[0]
            end = value.find(quote, 1)
            if end == -1:
                raise EnvParseError(
                    f"Unterminated quoted value at {filepath}:{lineno}: {raw_line!r}"
                )
            value = value[1:end]
        else:
            # Remove inline comment
            for i, ch in enumerate(value):
                if ch == "#" and (i == 0 or value[i - 1] == " "):
                    value = value[:i].strip()
                    break

        env[key] = value if value != "" else None

    return env


def _is_valid_key(key: str) -> bool:
    """Return True if the key contains only alphanumeric characters and underscores."""
    return bool(key) and all(ch.isalnum() or ch == "_" for ch in key)
