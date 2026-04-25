"""CLI command: envdiff overlap — show key overlap across multiple env files."""
from __future__ import annotations

import json
import sys

import click

from envdiff.env_diff_overlap import compute_overlap
from envdiff.overlap_formatter import format_overlap_result
from envdiff.parser import EnvParseError, parse_env_file


@click.command("overlap")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
@click.option("--no-colour", is_flag=True, default=False, help="Disable ANSI colour output.")
def overlap_cmd(files: tuple[str, ...], fmt: str, no_colour: bool) -> None:
    """Show key overlap statistics across multiple .env FILES."""
    envs: dict[str, dict[str, str]] = {}

    for path in files:
        try:
            envs[path] = parse_env_file(path)
        except EnvParseError as exc:
            click.echo(f"Error parsing {path}: {exc}", err=True)
            sys.exit(2)

    result = compute_overlap(envs)

    if fmt == "json":
        data = {
            "files": result.file_names,
            "universal": result.universal_keys,
            "partial": result.partial_keys,
            "unique": result.unique_keys,
            "rows": [
                {
                    "key": r.key,
                    "files": r.files,
                    "overlap_ratio": round(r.overlap_ratio, 4),
                }
                for r in result.rows
            ],
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(format_overlap_result(result, colour=not no_colour))

    if result.unique_keys or result.partial_keys:
        sys.exit(1)
