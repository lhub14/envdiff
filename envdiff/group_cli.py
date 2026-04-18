"""CLI command: envdiff group — group env keys by prefix."""
from __future__ import annotations

import sys

import click

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.env_group import group_by_prefix, format_group_result


@click.command("group")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--prefix",
    "prefixes",
    multiple=True,
    required=True,
    help="Prefix to group by (repeatable).",
)
@click.option(
    "--strip",
    is_flag=True,
    default=False,
    help="Strip the matched prefix from displayed key names.",
)
def group_cmd(env_file: str, prefixes: tuple, strip: bool) -> None:
    """Group keys in ENV_FILE by one or more prefixes."""
    try:
        env = parse_env_file(env_file)
    except EnvParseError as exc:
        click.echo(f"Error parsing {env_file}: {exc}", err=True)
        sys.exit(2)

    result = group_by_prefix(env, list(prefixes), strip_prefix=strip)
    click.echo(format_group_result(result))
