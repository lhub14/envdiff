"""CLI command: envdiff heatmap — show diff heatmap across multiple env pairs."""
from __future__ import annotations

import sys

import click

from envdiff.comparator import compare_envs
from envdiff.env_diff_heatmap import build_heatmap, has_hot_keys
from envdiff.heatmap_formatter import format_heatmap
from envdiff.ignore import build_ignore_matcher, load_ignore_file
from envdiff.parser import EnvParseError, parse_env_file


@click.command("heatmap")
@click.argument("base", type=click.Path(exists=True))
@click.argument("targets", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--ignore", "ignore_file", default=None, help="Path to ignore file.")
@click.option("--no-colour", is_flag=True, default=False, help="Disable colour output.")
@click.option(
    "--exit-code",
    is_flag=True,
    default=False,
    help="Exit 1 if any hot/critical keys found.",
)
def heatmap_cmd(
    base: str,
    targets: tuple[str, ...],
    ignore_file: str | None,
    no_colour: bool,
    exit_code: bool,
) -> None:
    """Show a heatmap of keys that differ most across TARGET env files vs BASE."""
    try:
        base_env = parse_env_file(base)
    except EnvParseError as exc:
        click.echo(f"Error parsing base file: {exc}", err=True)
        sys.exit(2)

    ignore_keys = load_ignore_file(ignore_file)
    matcher = build_ignore_matcher(ignore_keys)

    diffs = []
    for target_path in targets:
        try:
            target_env = parse_env_file(target_path)
        except EnvParseError as exc:
            click.echo(f"Error parsing {target_path}: {exc}", err=True)
            sys.exit(2)
        diffs.append(
            compare_envs(base_env, target_env, ignore=matcher, compare_values=True)
        )

    result = build_heatmap(diffs)
    click.echo(format_heatmap(result, colour=not no_colour))

    if exit_code and has_hot_keys(result):
        sys.exit(1)
