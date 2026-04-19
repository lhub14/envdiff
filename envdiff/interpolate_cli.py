"""CLI command: envdiff interpolate — resolve variable references in a .env file."""
from __future__ import annotations

import json
import sys

import click

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.env_interpolate import interpolate_env, has_issues


interpolate")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text",
              show_default=True, help="Output format.")
@click.option("--strict", is_flag=True, default=False,
              help="Exit 1 if any keys are unresolved or cyclic.")
def interpolate_cmd(env_file: str, fmt: str, strict: bool) -> None:
    """Resolve \${VAR} interpolation in ENV_FILE and print results."""
    try:
        env = parse_env_file(env_file)
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(2)

    result = interpolate_env(env)

    if fmt == "json":
        payload = {
            "resolved": result.resolved,
            "unresolved_keys": result.unresolved_keys,
            "cycles": result.cycles,
        }
        click.echo(json.dumps(payload, indent=2))
    else:
        for key, val in result.resolved.items():
            tag = ""
            if key in result.cycles:
                tag = "  # [cycle]"
            elif key in result.unresolved_keys:
                tag = "  # [unresolved]"
            click.echo(f"{key}={val}{tag}")
        if result.unresolved_keys:
            click.echo(f"\nUnresolved: {', '.join(result.unresolved_keys)}", err=True)
        if result.cycles:
            click.echo(f"Cycles detected: {', '.join(result.cycles)}", err=True)

    if strict and has_issues(result):
        sys.exit(1)
