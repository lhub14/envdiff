"""Compare multiple .env files against a base environment."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from envdiff.comparator import DiffResult, compare_envs
from envdiff.ignore import build_ignore_matcher
from envdiff.parser import parse_env_file


@dataclass
class MultiDiffResult:
    base: str
    results: Dict[str, DiffResult] = field(default_factory=dict)

    def any_differences(self) -> bool:
        from envdiff.comparator import has_differences
        return any(has_differences(r) for r in self.results.values())


def compare_many(
    base_path: Path,
    target_paths: List[Path],
    *,
    check_values: bool = True,
    ignore_keys: frozenset[str] = frozenset(),
) -> MultiDiffResult:
    """Compare base env against each target path."""
    matcher = build_ignore_matcher(ignore_keys)
    base_env = parse_env_file(base_path)

    result = MultiDiffResult(base=str(base_path))
    for target in target_paths:
        target_env = parse_env_file(target)
        diff = compare_envs(
            base_env,
            target_env,
            check_values=check_values,
            ignore=matcher,
        )
        result.results[str(target)] = diff
    return result
