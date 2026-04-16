"""Command-line interface for envdiff."""

import sys
from pathlib import Path

import click

from envdiff.comparator import compare_envs
from envdiff.formatter import format_diff
from envdiff.parser import EnvParseError, parse_env_file


@click.command()
@click.argument("base", type=click.Path(exists=True, dir_okay=False))
@click.argument("target", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--no-values",
    is_flag=True,
    default=False,
    help="Skip value comparison; only check for missing keys.",
)
@click.option(
    "--show-values",
    is_flag=True,
    default=False,
    help="Print actual values in mismatch output (may expose secrets).",
)
@click.option(
    "--exit-code",
    is_flag=True,
    default=False,
    help="Exit with code 1 when differences are found.",
)
def main(
    base: str,
    target: str,
    no_values: bool,
    show_values: bool,
    exit_code: bool,
) -> None:
    """Compare two .env files and report differences."""
    base_path = Path(base)
    target_path = Path(target)

    try:
        base_env = parse_env_file(base_path)
        target_env = parse_env_file(target_path)
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(2)

    result = compare_envs(
        base_env,
        target_env,
        base_name=base_path.name,
        target_name=target_path.name,
        check_values=not no_values,
    )

    click.echo(format_diff(result, show_values=show_values))

    if exit_code and result.has_differences:
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
