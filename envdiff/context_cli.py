"""CLI command: envdiff context — show diff with surrounding key context."""
from __future__ import annotations

import sys

import click

from envdiff.comparator import compare_envs
from envdiff.context_formatter import format_context_diff
from envdiff.env_diff_context import build_context_diff
from envdiff.parser import EnvParseError, parse_env_file


@click.command("context")
@click.argument("base", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option(
    "--lines", "-n",
    default=2,
    show_default=True,
    help="Number of context lines around each change.",
)
@click.option(
    "--no-color",
    is_flag=True,
    default=False,
    help="Disable ANSI colour output.",
)
@click.option(
    "--check-values / --no-check-values",
    default=True,
    show_default=True,
    help="Include value mismatches in context output.",
)
def context_cmd(
    base: str,
    target: str,
    lines: int,
    no_color: bool,
    check_values: bool,
) -> None:
    """Show diff between BASE and TARGET with surrounding key context."""
    try:
        base_env = parse_env_file(base)
        target_env = parse_env_file(target)
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(2)

    diff = compare_envs(base_env, target_env, check_values=check_values)
    result = build_context_diff(base_env, target_env, diff, context=lines)
    output = format_context_diff(result, no_color=no_color)
    click.echo(output)
    if not result.is_empty():
        sys.exit(1)
