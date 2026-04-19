"""Search keys/values across one or more .env files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class SearchMatch:
    file: str
    key: str
    value: str
    match_type: str  # 'key' | 'value' | 'both'


@dataclass
class SearchResult:
    pattern: str
    matches: List[SearchMatch] = field(default_factory=list)


def has_matches(result: SearchResult) -> bool:
    return bool(result.matches)


def search_envs(
    files: Dict[str, str],
    pattern: str,
    *,
    search_keys: bool = True,
    search_values: bool = True,
    case_sensitive: bool = False,
) -> SearchResult:
    """Search for *pattern* across parsed env dicts.

    Args:
        files: mapping of label -> file path.
        pattern: regex or plain substring pattern.
        search_keys: include key names in search.
        search_values: include values in search.
        case_sensitive: use case-sensitive matching.
    """
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        rx = re.compile(pattern, flags)
    except re.error as exc:
        raise ValueError(f"Invalid pattern {pattern!r}: {exc}") from exc

    result = SearchResult(pattern=pattern)

    for label, path in files.items():
        env = parse_env_file(path)
        for key, value in env.items():
            key_hit = search_keys and bool(rx.search(key))
            val_hit = search_values and bool(rx.search(value))
            if key_hit and val_hit:
                match_type = "both"
            elif key_hit:
                match_type = "key"
            elif val_hit:
                match_type = "value"
            else:
                continue
            result.matches.append(
                SearchMatch(file=label, key=key, value=value, match_type=match_type)
            )

    return result
