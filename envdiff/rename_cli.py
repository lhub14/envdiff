"""CLI command for rename detection."""
from __future__ import annotations

import sys
import click

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.rename import detect_renames, has_candidates
from envdiff.rename_formatter import format_rename_result


@click.command("rename")
@click.argument("base", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option(
    "--threshold",
    default=0.6,
    show_default=True,
    type=click.FloatRange(0.0, 1.0),
    help="Minimum similarity score (0-1) to suggest a rename.",
)
@click.option("--exit-code", is_flag=True, help="Exit 1 if any candidates found.")
def rename_cmd(base: str, target: str, threshold: float, exit_code: bool) -> None:
    """Suggest key renames between BASE and TARGET env files."""
    try:
        base_env = parse_env_file(base)
        target_env = parse_env_file(target)
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(2)

    result = detect_renames(base_env, target_env, threshold=threshold)
    click.echo(format_rename_result(result))

    if exit_code and has_candidates(result):
        sys.exit(1)
