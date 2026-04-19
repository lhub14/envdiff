"""Blame: annotate each diff entry with the git author who last changed it."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envdiff.comparator import DiffResult


@dataclass
class BlameEntry:
    key: str
    kind: str  # "missing_in_target" | "missing_in_base" | "mismatch"
    author: Optional[str] = None
    commit: Optional[str] = None


@dataclass
class BlameResult:
    entries: list[BlameEntry] = field(default_factory=list)


def _git_blame_key(filepath: Path, key: str) -> tuple[Optional[str], Optional[str]]:
    """Return (author, short_commit) for the line defining *key* in *filepath*."""
    try:
        raw = subprocess.check_output(
            ["git", "blame", "-p", str(filepath)],
            stderr=subprocess.DEVNULL,
        ).decode(errors="replace")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None

    commit: Optional[str] = None
    author: Optional[str] = None
    target_line: Optional[str] = None

    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("author ") and target_line == "pending":
            author = line[len("author "):].strip()
        if line.startswith("\t") and target_line is None:
            content = line[1:]
            if content.startswith(key + "=") or content.startswith(key + " ="):
                commit = lines[i - (i % 1)]  # placeholder; resolved below
                target_line = "pending"
        if len(line) == 40 and all(c in "0123456789abcdef" for c in line[:8]):
            current_commit = line[:8]
        if target_line == "pending" and author:
            commit = current_commit  # type: ignore[possibly-undefined]
            break
        i += 1

    return author, commit


def blame_diff(diff: DiffResult, base_path: Path, target_path: Path) -> BlameResult:
    entries: list[BlameEntry] = []

    for key in diff.missing_in_target:
        author, commit = _git_blame_key(base_path, key)
        entries.append(BlameEntry(key=key, kind="missing_in_target", author=author, commit=commit))

    for key in diff.missing_in_base:
        author, commit = _git_blame_key(target_path, key)
        entries.append(BlameEntry(key=key, kind="missing_in_base", author=author, commit=commit))

    for key in diff.mismatched:
        author, commit = _git_blame_key(base_path, key)
        entries.append(BlameEntry(key=key, kind="mismatch", author=author, commit=commit))

    return BlameResult(entries=entries)
