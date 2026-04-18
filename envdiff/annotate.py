"""Annotate an env file with inline comments describing diff status."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from envdiff.comparator import DiffResult


def annotate_lines(
    base_path: Path,
    diff: DiffResult,
    target_label: str = "target",
) -> list[str]:
    """Return lines of *base_path* with trailing annotations injected."""
    raw = base_path.read_text(encoding="utf-8")
    out: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            out.append(line)
            continue
        if "=" not in stripped:
            out.append(line)
            continue
        key = stripped.split("=", 1)[0].strip()
        if key in diff.missing_in_target:
            out.append(f"{line}  # MISSING in {target_label}")
        elif key in diff.missing_in_base:
            out.append(f"{line}  # EXTRA (not in {target_label})")
        elif key in diff.mismatched:
            out.append(f"{line}  # MISMATCH with {target_label}")
        else:
            out.append(line)
    return out


def write_annotated(
    base_path: Path,
    diff: DiffResult,
    output_path: Optional[Path] = None,
    target_label: str = "target",
) -> str:
    """Write annotated content to *output_path* (or return as string)."""
    lines = annotate_lines(base_path, diff, target_label)
    content = "\n".join(lines) + "\n"
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    return content
