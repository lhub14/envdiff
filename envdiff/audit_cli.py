"""CLI sub-commands for audit log management."""
from __future__ import annotations

from pathlib import Path

import click

from envdiff.audit import load_log
from envdiff.audit_formatter import format_audit_log

DEFAULT_LOG = Path(".envdiff_audit.log")


@click.group("audit")
def audit_group() -> None:
    """Manage the envdiff audit log."""


@audit_group.command("show")
@click.option("--log", default=str(DEFAULT_LOG), show_default=True, help="Path to audit log file.")
@click.option("--tail", default=0, help="Show last N entries (0 = all).")
def show_audit(log: str, tail: int) -> None:
    """Display recorded audit entries."""
    path = Path(log)
    if not path.exists():
        click.echo("Log file not found — no entries to display.")
        return
    entries = load_log(path)
    if tail > 0:
        entries = entries[-tail:]
    click.echo(format_audit_log(entries))


@audit_group.command("clear")
@click.option("--log", default=str(DEFAULT_LOG), show_default=True, help="Path to audit log file.")
@click.confirmation_option(prompt="Delete all audit entries?")
def clear_audit(log: str) -> None:
    """Remove all entries from the audit log."""
    p = Path(log)
    if p.exists():
        p.write_text("", encoding="utf-8")
        click.echo(f"Cleared {log}")
    else:
        click.echo("Log file not found — nothing to clear.")
