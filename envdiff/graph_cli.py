"""CLI command: envdiff graph — show key presence across multiple env files."""
from __future__ import annotations

import sys
import click

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.graph import build_graph, shared_ratio
from envdiff.graph_formatter import format_graph


@click.command("graph")
@click.argument("files", nargs=-1, required=True, metavar="FILE...")
@click.option("--no-color", is_flag=True, default=False, help="Disable colour output.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output JSON.")
def graph_cmd(files: tuple[str, ...], no_color: bool, as_json: bool) -> None:
    """Show which keys are shared, partial, or unique across FILE(s)."""
    envs: dict[str, dict[str, str]] = {}
    for path in files:
        try:
            envs[path] = parse_env_file(path)
        except EnvParseError as exc:
            click.echo(f"Error parsing {path}: {exc}", err=True)
            sys.exit(2)
        except FileNotFoundError:
            click.echo(f"File not found: {path}", err=True)
            sys.exit(2)

    result = build_graph(envs)

    if as_json:
        import json
        payload = {
            "universal": sorted(result.universal),
            "partial": {k: sorted(v) for k, v in result.partial.items()},
            "unique": {k: v for k, v in result.unique.items()},
            "shared_ratio": round(shared_ratio(result, len(envs)), 4),
        }
        click.echo(json.dumps(payload, indent=2))
        sys.exit(0)

    click.echo(format_graph(result, no_color=no_color))
    ratio = shared_ratio(result, len(envs))
    click.echo(f"\nShared ratio: {ratio:.0%}")
    sys.exit(0)
