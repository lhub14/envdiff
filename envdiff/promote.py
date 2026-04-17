"""Promote keys from one env file to another, merging missing keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envdiff.parser import parse_env_file


@dataclass
class PromoteResult:
    source: str
    target: str
    added: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    output: Dict[str, str] = field(default_factory=dict)


def has_changes(result: PromoteResult) -> bool:
    return bool(result.added)


def promote_env(
    source_path: str | Path,
    target_path: str | Path,
    *,
    overwrite: bool = False,
    dry_run: bool = False,
) -> PromoteResult:
    """Promote keys from source into target.

    Keys already present in target are skipped unless overwrite=True.
    When dry_run=True the target file is not written.
    """
    source = parse_env_file(Path(source_path))
    target = parse_env_file(Path(target_path))

    result = PromoteResult(
        source=str(source_path),
        target=str(target_path),
        output=dict(target),
    )

    for key, value in source.items():
        if key in target and not overwrite:
            result.skipped.append(key)
        else:
            if key not in target or target[key] != value:
                result.added.append(key)
            result.output[key] = value

    if not dry_run and result.added:
        _write_env(Path(target_path), result.output)

    return result


def _write_env(path: Path, env: Dict[str, str]) -> None:
    lines = [f"{k}={_quote(v)}" for k, v in env.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _quote(value: str) -> str:
    if " " in value or "#" in value or not value:
        return f'"{value}"'
    return value
