"""CLI command: envdiff prune — remove stale keys not present in any reference file."""
from __future__ import annotations

from pathlib import Path
from typing import List

import click

from envdiff.env_prune import has_pruned, prune_env


@click.command("prune")
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument(
    "references",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be pruned without modifying the file.",
)
@click.option(
    "--quiet",
    is_flag=True,
    default=False,
    help="Suppress output; use exit code only.",
)
def prune_cmd(
    source: Path,
    references: List[Path],
    dry_run: bool,
    quiet: bool,
) -> None:
    """Remove keys from SOURCE that are absent from all REFERENCES.

    Exits 0 when nothing is pruned, 1 when keys are removed (or would be).
    """
    from envdiff.parser import EnvParseError

    try:
        result = prune_env(source, list(references), dry_run=dry_run)
    except EnvParseError as exc:
        raise click.ClickException(str(exc)) from exc

    if not quiet:
        if not has_pruned(result):
            click.echo(f"No stale keys found in {source}.")
        else:
            action = "Would prune" if dry_run else "Pruned"
            for key in result.pruned:
                click.echo(f"  {action}: {key}")
            click.echo(
                f"{action} {len(result.pruned)} key(s) from {source}."
            )

    raise SystemExit(1 if has_pruned(result) else 0)
