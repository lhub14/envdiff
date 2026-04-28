"""CLI command: envdiff radar"""
from __future__ import annotations

import json
import sys

import click

from envdiff.env_diff_radar import build_radar, RadarResult
from envdiff.radar_formatter import format_radar_result
from envdiff.ignore import load_ignore_file, build_ignore_matcher


def _to_json(result: RadarResult) -> str:
    data = {
        "base": result.base_label,
        "entries": [
            {
                "label": e.label,
                "score": e.score(),
                "axes": [{"name": a.name, "value": a.value, "raw": a.raw} for a in e.axes],
            }
            for e in result.entries
        ],
    }
    return json.dumps(data, indent=2)


@click.command("radar")
@click.argument("base", type=click.Path(exists=True))
@click.argument("targets", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--ignore-file", default=None, help="Path to .envignore file.")
@click.option("--format", "fmt", default="text", type=click.Choice(["text", "json"]), show_default=True)
@click.option("--no-colour", is_flag=True, default=False, help="Disable ANSI colour output.")
def radar_cmd(base: str, targets: tuple[str, ...], ignore_file: str | None, fmt: str, no_colour: bool) -> None:
    """Show radar metrics comparing BASE against each TARGET."""
    ignore_keys: frozenset[str] = frozenset()
    if ignore_file:
        raw = load_ignore_file(ignore_file)
        matcher = build_ignore_matcher(raw)
        ignore_keys = frozenset(matcher)

    target_map = {t: t for t in targets}
    result = build_radar(base, target_map, ignore=ignore_keys)

    if fmt == "json":
        click.echo(_to_json(result))
        sys.exit(0)

    click.echo(format_radar_result(result, colour=not no_colour))
    any_low = any(e.score() < 0.9 for e in result.entries)
    sys.exit(1 if any_low else 0)
