"""CLI entry point for the lint command."""
from __future__ import annotations
import sys
import click
from .lint import lint_env_file


def _severity_label(s: str) -> str:
    return click.style(s.upper(), fg="red" if s == "error" else "yellow")


@click.command("lint")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=False))
@click.option("--strict", is_flag=True, default=False, help="Treat warnings as errors.")
def lint_cmd(files: tuple[str, ...], strict: bool) -> None:
    """Lint one or more .env files for common issues."""
    any_issues = False
    for path in files:
        result = lint_env_file(path)
        if not result.has_issues:
            click.echo(f"{path}: OK")
            continue
        any_issues = True
        for issue in result.issues:
            label = _severity_label(issue.severity)
            key_part = f" [{issue.key}]" if issue.key else ""
            click.echo(f"{path}:{issue.line}: {label}{key_part} {issue.message}")
        if strict and result.warnings and not result.errors:
            any_issues = True
    if any_issues:
        sys.exit(1)
