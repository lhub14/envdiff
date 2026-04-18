"""CLI command: envdiff split"""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

import click

from envdiff.env_split import split_env_file, write_split_files, has_unmatched
from envdiff.parser import EnvParseError


@click.command("split")
@click.argument("env_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--prefix",
    "prefixes",
    multiple=True,
    required=True,
    help="Key prefix to split on (repeatable).",
)
@click.option(
    "--output-dir",
    "-o",
    default="split_envs",
    show_default=True,
    type=click.Path(path_type=Path),
    help="Directory to write split files into.",
)
@click.option(
    "--strip-prefix",
    is_flag=True,
    default=False,
    help="Remove the matched prefix from keys in the output file.",
)
@click.option(
    "--warn-unmatched/--no-warn-unmatched",
    default=True,
    show_default=True,
    help="Print a warning when keys match no prefix.",
)
def split_cmd(
    env_file: Path,
    prefixes: Tuple[str, ...],
    output_dir: Path,
    strip_prefix: bool,
    warn_unmatched: bool,
) -> None:
    """Split ENV_FILE into separate files grouped by key prefix."""
    try:
        result = split_env_file(env_file, list(prefixes), strip_prefix=strip_prefix)
    except EnvParseError as exc:
        raise click.ClickException(str(exc)) from exc

    written = write_split_files(result, output_dir)
    for path in written:
        click.echo(f"wrote {path}")

    if warn_unmatched and has_unmatched(result):
        keys = ", ".join(sorted(result.unmatched))
        click.echo(f"warning: {len(result.unmatched)} unmatched key(s): {keys}", err=True)
