"""Radar (spider-chart data) comparison across multiple .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import compare_envs, DiffResult
from envdiff.parser import parse_env_file


@dataclass
class RadarAxis:
    name: str          # metric label
    value: float       # 0.0 – 1.0
    raw: int           # raw count used to derive value


@dataclass
class RadarEntry:
    label: str
    axes: List[RadarAxis] = field(default_factory=list)

    def score(self) -> float:
        if not self.axes:
            return 0.0
        return round(sum(a.value for a in self.axes) / len(self.axes), 4)


@dataclass
class RadarResult:
    base_label: str
    entries: List[RadarEntry] = field(default_factory=list)


def _safe_ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 1.0


def build_radar(
    base_path: str,
    targets: Dict[str, str],
    ignore: frozenset[str] | None = None,
) -> RadarResult:
    """Compare *base_path* against each target and return per-file radar data."""
    ignore = ignore or frozenset()
    base_env = parse_env_file(base_path)
    total_keys = len([k for k in base_env if k not in ignore])
    result = RadarResult(base_label=base_path)

    for label, target_path in targets.items():
        target_env = parse_env_file(target_path)
        diff: DiffResult = compare_envs(base_env, target_env, ignore_keys=ignore)

        present = total_keys - len(diff.missing_in_target)
        match = present - len(diff.mismatched)

        axes = [
            RadarAxis("coverage", _safe_ratio(present, total_keys), present),
            RadarAxis("consistency", _safe_ratio(match, total_keys), match),
            RadarAxis(
                "extra_keys",
                _safe_ratio(
                    max(0, total_keys - len(diff.missing_in_base)),
                    max(total_keys, 1),
                ),
                len(diff.missing_in_base),
            ),
        ]
        result.entries.append(RadarEntry(label=label, axes=axes))

    return result
