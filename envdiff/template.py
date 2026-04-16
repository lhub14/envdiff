"""Generate .env.template files from existing env files."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from envdiff.parser import parse_env_file
from envdiff.redact import is_sensitive


class TemplateError(Exception):
    pass


def generate_template(
    env: dict[str, str],
    include_values: bool = False,
    placeholder: str = "",
) -> str:
    """Return template content from an env dict."""
    lines: list[str] = []
    for key, value in sorted(env.items()):
        if include_values and not is_sensitive(key):
            lines.append(f"{key}={value}")
        else:
            lines.append(f"{key}={placeholder}")
    return "\n".join(lines) + "\n" if lines else ""


def template_from_file(
    path: str | Path,
    include_values: bool = False,
    placeholder: str = "",
) -> str:
    """Parse *path* and return a template string."""
    env = parse_env_file(Path(path))
    return generate_template(env, include_values=include_values, placeholder=placeholder)


def write_template(
    content: str,
    dest: str | Path,
) -> None:
    """Write *content* to *dest*, creating parent dirs as needed."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)
