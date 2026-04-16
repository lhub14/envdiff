"""Write report content to file or stdout."""
from __future__ import annotations

import sys
from pathlib import Path

from envdiff.reporter import Report


def write_report(report: Report, output_path: str | None = None) -> None:
    """Write report content to *output_path* or stdout."""
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(report.content, encoding="utf-8")
        except OSError as exc:
            print(f"Error writing report to {path}: {exc}", file=sys.stderr)
            raise
    else:
        click_or_print(report.content)


def click_or_print(text: str) -> None:
    """Print text to stdout, one line at a time."""
    for line in text.splitlines():
        print(line)
