"""Compare parsed .env dictionaries and report differences."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class DiffResult:
    """Holds the result of comparing two .env files."""

    base_name: str
    target_name: str
    missing_in_target: List[str] = field(default_factory=list)
    missing_in_base: List[str] = field(default_factory=list)
    value_mismatches: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.missing_in_target or self.missing_in_base or self.value_mismatches
        )


def compare_envs(
    base: Dict[str, Optional[str]],
    target: Dict[str, Optional[str]],
    base_name: str = "base",
    target_name: str = "target",
    check_values: bool = True,
) -> DiffResult:
    """Compare two env dicts and return a DiffResult.

    Args:
        base: The reference environment mapping.
        target: The environment mapping to compare against base.
        base_name: Label for the base environment.
        target_name: Label for the target environment.
        check_values: When True, also flag keys whose values differ.

    Returns:
        A DiffResult describing all detected differences.
    """
    base_keys: Set[str] = set(base.keys())
    target_keys: Set[str] = set(target.keys())

    result = DiffResult(base_name=base_name, target_name=target_name)
    result.missing_in_target = sorted(base_keys - target_keys)
    result.missing_in_base = sorted(target_keys - base_keys)

    if check_values:
        common_keys = base_keys & target_keys
        for key in sorted(common_keys):
            if base[key] != target[key]:
                result.value_mismatches[key] = (base[key], target[key])

    return result
