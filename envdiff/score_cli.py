"""CLI command: envdiff score — show health score for a target env vs base."""
from __future__ import annotations

import sys

import click

from envdiff.comparator import compare_envs
from envdiff.parser import parse_env_file, EnvParseError
from envdiff.score import compute_score
from envdiff.score_formatter import format_score


@click.command("score")
@click.argument("base", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--no-colour", is_flag=True, default=False, help="Disable ANSI colour.")
@click.option("--fail-below", type=float, default=None, metavar="N",
              help="Exit 1 if score is below N.")
def score_cmd(base: str, target: str, no_colour: bool, fail_below: float | None) -> None:
    """Show a health score comparing TARGET against BASE."""
    try:
        base_env = parse_env_file(base)
        target_env = parse_env_file(target)
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(2)

    diff = compare_envs(base_env, target_env)
    result = compute_score(base_env, diff)
    click.echo(format_score(result, colour=not no_colour))

    if fail_below is not None and result.score < fail_below:
        sys.exit(1)
