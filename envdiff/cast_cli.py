"""CLI command: envdiff cast — parse and type-cast an env file."""
from __future__ import annotations

import sys

import click

from envdiff.env_cast import cast_env, has_issues
from envdiff.cast_formatter import format_cast_result
from envdiff.parser import parse_env_file, EnvParseError


@click.command("cast")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--schema",
    "schema_pairs",
    multiple=True,
    metavar="KEY=TYPE",
    help="Type hint, e.g. PORT=int. Repeat for multiple keys.",
)
@click.option("--no-colour", is_flag=True, default=False)
def cast_cmd(env_file: str, schema_pairs: tuple[str, ...], no_colour: bool) -> None:
    """Cast values in ENV_FILE to typed Python objects.

    Supported types: int, float, bool, str (default).
    """
    try:
        env = parse_env_file(env_file)
    except EnvParseError as exc:
        click.echo(f"Error parsing env file: {exc}", err=True)
        sys.exit(2)

    schema: dict[str, str] = {}
    for pair in schema_pairs:
        if "=" not in pair:
            click.echo(f"Invalid schema pair (expected KEY=TYPE): {pair!r}", err=True)
            sys.exit(2)
        k, t = pair.split("=", 1)
        schema[k.strip()] = t.strip()

    result = cast_env(env, schema)
    click.echo(format_cast_result(result, colour=not no_colour))
    sys.exit(1 if has_issues(result) else 0)
