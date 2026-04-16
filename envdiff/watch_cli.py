"""CLI integration for the watch feature."""
from __future__ import annotations

import click
from pathlib import Path
from typing import List

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.comparator import compare_envs
from envdiff.formatter import format_diff
from envdiff.watch import watch_files


def _run_diff(base: Path, target: Path, no_values: bool) -> None:
    click.echo(f"\n[envdiff] Change detected — comparing {base} vs {target}")
    try:
        base_env = parse_env_file(base)
        target_env = parse_env_file(target)
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        return
    result = compare_envs(base_env, target_env, compare_values=not no_values)
    click.echo(format_diff(result))


@click.command("watch")
@click.argument("base", type=click.Path(exists=True, path_type=Path))
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.option("--interval", default=2.0, show_default=True, help="Poll interval in seconds.")
@click.option("--no-values", is_flag=True, default=False, help="Skip value comparison.")
def watch_cmd(base: Path, target: Path, interval: float, no_values: bool) -> None:
    """Watch BASE and TARGET .env files and re-diff on change."""
    click.echo(f"[envdiff] Watching {base} and {target} (interval={interval}s) — Ctrl+C to stop")
    _run_diff(base, target, no_values)

    def on_change() -> None:
        _run_diff(base, target, no_values)

    try:
        watch_files([base, target], on_change, interval=interval)
    except KeyboardInterrupt:
        click.echo("\n[envdiff] Watch stopped.")
