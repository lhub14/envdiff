"""CLI command for normalizing a .env file."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envdiff.env_normalize import has_changes, normalize_env, write_normalized
from envdiff.normalize_formatter import format_normalize_result
from envdiff.parser import EnvParseError


@click.command("normalize")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--write", "-w", is_flag=True, help="Write normalized output back to file.")
@click.option("--check", is_flag=True, help="Exit 1 if file is not normalized (CI mode).")
@click.option("--no-colour", is_flag=True, default=False, help="Disable colour output.")
def normalize_cmd(env_file: str, write: bool, check: bool, no_colour: bool) -> None:
    """Normalize a .env file in place or report what would change."""
    path = Path(env_file)
    try:
        result = normalize_env(path)
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(2)

    click.echo(format_normalize_result(result, colour=not no_colour))

    if write and has_changes(result):
        write_normalized(result, path)
        click.echo(f"Written: {path}")

    if check and has_changes(result):
        sys.exit(1)
