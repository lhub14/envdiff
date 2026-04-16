"""CLI commands for baseline snapshot management."""
from __future__ import annotations

from pathlib import Path

import click

from envdiff.baseline import BaselineError, diff_against_baseline, list_baselines, save_baseline
from envdiff.comparator import has_differences
from envdiff.formatter import format_diff
from envdiff.parser import EnvParseError, parse_env_file

DEFAULT_STORE = Path(".envdiff_baselines.json")


@click.group("baseline")
def baseline_group() -> None:
    """Manage .env baseline snapshots."""


@baseline_group.command("save")
@click.argument("label")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--store", default=str(DEFAULT_STORE), show_default=True)
def save_cmd(label: str, env_file: str, store: str) -> None:
    """Save current ENV_FILE as a named baseline LABEL."""
    try:
        env = parse_env_file(Path(env_file))
    except EnvParseError as exc:
        raise click.ClickException(str(exc))
    try:
        save_baseline(label, env, Path(store))
    except BaselineError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Baseline '{label}' saved.")


@baseline_group.command("diff")
@click.argument("label")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--store", default=str(DEFAULT_STORE), show_default=True)
@click.option("--no-values", is_flag=True, default=False)
def diff_cmd(label: str, env_file: str, store: str, no_values: bool) -> None:
    """Diff ENV_FILE against saved baseline LABEL."""
    try:
        env = parse_env_file(Path(env_file))
    except EnvParseError as exc:
        raise click.ClickException(str(exc))
    try:
        result = diff_against_baseline(label, env, Path(store), check_values=not no_values)
    except BaselineError as exc:
        raise click.ClickException(str(exc))
    click.echo(format_diff(result))
    if has_differences(result):
        raise SystemExit(1)


@baseline_group.command("list")
@click.option("--store", default=str(DEFAULT_STORE), show_default=True)
def list_cmd(store: str) -> None:
    """List all saved baselines."""
    labels = list_baselines(Path(store))
    if not labels:
        click.echo("No baselines saved.")
    else:
        for lbl in labels:
            click.echo(lbl)
