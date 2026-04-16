"""Export parsed env data to various formats (JSON, dotenv, shell export)."""
from __future__ import annotations

import json
from typing import Dict


class ExportError(Exception):
    pass


SUPPORTED_FORMATS = ("json", "dotenv", "shell")


def export_env(env: Dict[str, str], fmt: str) -> str:
    """Serialize *env* dict to the requested format string."""
    if fmt not in SUPPORTED_FORMATS:
        raise ExportError(
            f"Unsupported format {fmt!r}. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    if fmt == "json":
        return _to_json(env)
    if fmt == "dotenv":
        return _to_dotenv(env)
    if fmt == "shell":
        return _to_shell(env)


def _to_json(env: Dict[str, str]) -> str:
    return json.dumps(env, indent=2, sort_keys=True)


def _to_dotenv(env: Dict[str, str]) -> str:
    lines = []
    for key in sorted(env):
        value = env[key]
        if any(c in value for c in (" ", "\t", "#", '"', "'")):
            value = '"' + value.replace('"', '\\"') + '"'
        lines.append(f"{key}={value}")
    return "\n".join(lines)


def _to_shell(env: Dict[str, str]) -> str:
    lines = []
    for key in sorted(env):
        value = env[key].replace("'", "'\"'\"'")
        lines.append(f"export {key}='{value}'")
    return "\n".join(lines)
