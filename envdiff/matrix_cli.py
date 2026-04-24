"""CLI command: envdiff matrix — show key-by-environment presence matrix."""
from __future__ import annotations

import sys
from typing import Tuple

import click

from envdiff.env_diff_matrix import build_matrix, MatrixResult
from envdiff.matrix_formatter import format_matrix
from envdiff.parser import parse_env_file, EnvParseError


def _load_envs(files: Tuple[str, ...]) -> dict:
    envs = {}
    for path in files:
        try:
            envs[path] = parse_env_file(path)
        except EnvParseError as exc:
            click.echo(f"Error parsing {path}: {exc}", err=True)
            sys.exit(2)
    return envs


@click.command("matrix")
@click.argument("files", nargs=-1, required=True, metavar="FILE...")
@click.option("--gaps-only", is_flag=True, default=False, help="Show only keys with missing entries.")
@click.option("--no-color", is_flag=True, default=False, help="Disable ANSI colour output.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def matrix_cmd(files: Tuple[str, ...], gaps_only: bool, no_color: bool, as_json: bool) -> None:
    """Display a key-by-environment presence/value matrix."""
    envs = _load_envs(files)
    result: MatrixResult = build_matrix(envs)

    if gaps_only:
        result.rows = [r for r in result.rows if not r.is_complete or not r.is_uniform]

    if as_json:
        import json
        data = {
            "env_names": result.env_names,
            "rows": [
                {
                    "key": r.key,
                    "complete": r.is_complete,
                    "uniform": r.is_uniform,
                    "cells": {
                        name: {"present": c.present, "value": c.value}
                        for name, c in r.cells.items()
                    },
                }
                for r in result.rows
            ],
        }
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(format_matrix(result, no_color=no_color))

    if result.has_gaps or result.has_mismatches:
        sys.exit(1)
