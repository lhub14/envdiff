"""Detect and remove keys from a .env file that are not present in a reference set."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set

from envdiff.parser import parse_env_file


@dataclass
class PruneResult:
    source_file: str
    reference_files: List[str]
    kept: Dict[str, str] = field(default_factory=dict)
    pruned: List[str] = field(default_factory=list)
    output_lines: List[str] = field(default_factory=list)


def has_pruned(result: PruneResult) -> bool:
    return len(result.pruned) > 0


def _quote_if_needed(value: str) -> str:
    if " " in value or "#" in value or value == "":
        return f'"{value}"'
    return value


def prune_env(
    source: Path,
    references: List[Path],
    dry_run: bool = False,
) -> PruneResult:
    """Remove keys from *source* that do not appear in any of *references*."""
    source_env = parse_env_file(source)

    allowed: Set[str] = set()
    for ref in references:
        allowed.update(parse_env_file(ref).keys())

    result = PruneResult(
        source_file=str(source),
        reference_files=[str(r) for r in references],
    )

    raw_lines = source.read_text(encoding="utf-8").splitlines()

    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            result.output_lines.append(line)
            continue
        if "=" not in stripped:
            result.output_lines.append(line)
            continue
        key = stripped.split("=", 1)[0].strip()
        if key in allowed:
            result.kept[key] = source_env.get(key, "")
            result.output_lines.append(line)
        else:
            result.pruned.append(key)

    if not dry_run and result.pruned:
        source.write_text("\n".join(result.output_lines) + "\n", encoding="utf-8")

    return result
