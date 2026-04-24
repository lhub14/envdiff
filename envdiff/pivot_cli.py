"""CLI command: envdiff pivot — show a key-vs-file comparison matrix."""
from __future__ import annotations

import sys

import click

from envdiff.parser import EnvParseError, parse_env_file
from envdiff.env_pivot import pivot_envs
from envdiff.pivot_formatter import format_pivot


@click.command("pivot")
@click.argument("files", nargs=-1, required=True, metavar="FILE...")
@click.option("--no-colour", is_flag=True, default=False, help="Disable colour output.")
@click.option("--gaps-only", is_flag=True, default=False, help="Show only keys missing in at least one file.")
@click.option("--mismatches-only", is_flag=True, default=False, help="Show only keys with differing values.")
def pivot_cmd(files: tuple, no_colour: bool, gaps_only: bool, mismatches_only: bool) -> None:
    """Display a pivot table of keys across multiple .env FILES."""
    envs = {}
    for path in files:
        try:
            envs[path] = parse_env_file(path)
        except EnvParseError as exc:
            click.echo(f"Error parsing {path}: {exc}", err=True)
            sys.exit(2)
        except OSError as exc:
            click.echo(f"Cannot read {path}: {exc}", err=True)
            sys.exit(2)

    result = pivot_envs(envs)

    if gaps_only:
        result.rows = [r for r in result.rows if not r.is_complete]
    if mismatches_only:
        result.rows = [r for r in result.rows if not r.is_uniform]

    output = format_pivot(result, colour=not no_colour)
    click.echo(output, nl=False)

    if result.has_gaps or result.has_mismatches:
        sys.exit(1)
