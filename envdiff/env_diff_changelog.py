"""Generate a human-readable changelog from a sequence of diff history entries.

Builds a structured changelog that groups changes by date and summarises
what keys were added, removed, or changed between consecutive snapshots.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.diff_history import HistoryEntry


@dataclass
class ChangelogEntry:
    """A single changelog record derived from a history entry."""

    timestamp: str
    label: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    note: Optional[str] = None

    @property
    def is_clean(self) -> bool:
        """Return True when no changes are recorded."""
        return not (self.added or self.removed or self.changed)

    @property
    def total(self) -> int:
        """Total number of changed keys."""
        return len(self.added) + len(self.removed) + len(self.changed)


@dataclass
class ChangelogResult:
    """Ordered collection of changelog entries."""

    entries: List[ChangelogEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(not e.is_clean for e in self.entries)


def build_changelog(history: List[HistoryEntry]) -> ChangelogResult:
    """Convert a list of *HistoryEntry* objects into a *ChangelogResult*.

    Each history entry already carries the diff counts; we expand them into
    named key lists using the ``missing_in_target``, ``missing_in_base``, and
    ``mismatched`` fields that are stored on the entry's diff snapshot.
    """
    entries: List[ChangelogEntry] = []

    for h in history:
        added: List[str] = []
        removed: List[str] = []
        changed: List[str] = []

        diff = getattr(h, "diff", None)
        if diff is not None:
            # missing_in_target means the key exists in base but not target → removed
            removed = sorted(getattr(diff, "missing_in_target", []))
            # missing_in_base means the key exists in target but not base → added
            added = sorted(getattr(diff, "missing_in_base", []))
            changed = sorted(getattr(diff, "mismatched", []))

        entry = ChangelogEntry(
            timestamp=h.timestamp,
            label=getattr(h, "label", ""),
            added=added,
            removed=removed,
            changed=changed,
        )
        entries.append(entry)

    return ChangelogResult(entries=entries)


def changelog_to_text(result: ChangelogResult) -> str:
    """Render a *ChangelogResult* as plain text."""
    if not result.entries:
        return "No history entries found."

    lines: List[str] = []
    for entry in result.entries:
        header = f"[{entry.timestamp}]  {entry.label}" if entry.label else f"[{entry.timestamp}]"
        lines.append(header)
        if entry.is_clean:
            lines.append("  (no changes)")
        else:
            for k in entry.added:
                lines.append(f"  + {k}")
            for k in entry.removed:
                lines.append(f"  - {k}")
            for k in entry.changed:
                lines.append(f"  ~ {k}")
        lines.append("")

    return "\n".join(lines).rstrip()


def changelog_to_json(result: ChangelogResult) -> Dict:
    """Serialise a *ChangelogResult* to a JSON-compatible dict."""
    return {
        "has_changes": result.has_changes,
        "entries": [
            {
                "timestamp": e.timestamp,
                "label": e.label,
                "added": e.added,
                "removed": e.removed,
                "changed": e.changed,
                "total": e.total,
                "clean": e.is_clean,
            }
            for e in result.entries
        ],
    }
