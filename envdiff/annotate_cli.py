"""CLI command: envdiff annotate."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.comparator import compare_envs
from envdiff.annotate import write_annotated


@click.command("annotate")
@click.argument("base", type=click.Path(exists=True, dir_okay=False))
@click.argument("target", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False),
    default=None,
    help="Write annotated output to this file instead of stdout.",
)
@click.option(
    "--no-values",
    is_flag=True,
    default=False,
    help="Skip value-mismatch annotations.",
)
def annotate_cmd(base: str, target: str, output: str | None, no_values: bool) -> None:
    """Annotate BASE with diff status relative to TARGET."""
    try:
        base_env = parse_env_file(Path(base))
        target_env = parse_env_file(Path(target))
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(2)

    diff = compare_envs(base_env, target_env, check_values=not no_values)
    out_path = Path(output) if output else None
    content = write_annotated(
        Path(base), diff, output_path=out_path, target_label=Path(target).name
    )
    if not out_path:
        click.echo(content, nl=False)
