"""CLI commands for env snapshots."""
from __future__ import annotations

import json
from pathlib import Path

import click

from envdiff.snapshot import (
    SnapshotError,
    take_snapshot,
    save_snapshot,
    load_snapshots,
    diff_snapshots,
)

DEFAULT_STORE = ".envdiff_snapshots.jsonl"


@click.group("snapshot")
def snapshot_group() -> None:
    """Capture and compare point-in-time env snapshots."""


@snapshot_group.command("capture")
@click.argument("env_file")
@click.option("--store", default=DEFAULT_STORE, show_default=True)
def capture_cmd(env_file: str, store: str) -> None:
    """Capture a snapshot of ENV_FILE."""
    try:
        snap = take_snapshot(env_file)
    except SnapshotError as exc:
        raise click.ClickException(str(exc))
    save_snapshot(snap, store)
    click.echo(f"Snapshot captured: {snap['captured_at']} ({len(snap['keys'])} keys)")


@snapshot_group.command("list")
@click.option("--store", default=DEFAULT_STORE, show_default=True)
def list_cmd(store: str) -> None:
    """List all captured snapshots."""
    snaps = load_snapshots(store)
    if not snaps:
        click.echo("No snapshots found.")
        return
    for i, s in enumerate(snaps):
        click.echo(f"[{i}] {s['captured_at']}  {s['file']}  ({len(s['keys'])} keys)")


@snapshot_group.command("diff")
@click.option("--store", default=DEFAULT_STORE, show_default=True)
@click.option("--older", "older_idx", default=-2, show_default=True, type=int)
@click.option("--newer", "newer_idx", default=-1, show_default=True, type=int)
@click.option("--json", "as_json", is_flag=True)
def diff_cmd(store: str, older_idx: int, newer_idx: int, as_json: bool) -> None:
    """Diff two snapshots (default: last two)."""
    snaps = load_snapshots(store)
    if len(snaps) < 2:
        raise click.ClickException("Need at least 2 snapshots to diff.")
    older = snaps[older_idx]
    newer = snaps[newer_idx]
    result = diff_snapshots(older, newer)
    if as_json:
        click.echo(json.dumps(result, indent=2))
        return
    for key in result["added"]:
        click.echo(f"+ {key}={result['added'][key]}")
    for key in result["removed"]:
        click.echo(f"- {key}={result['removed'][key]}")
    for key, vals in result["changed"].items():
        click.echo(f"~ {key}: {vals['old']} -> {vals['new']}")
    if not any(result.values()):
        click.echo("No changes between snapshots.")
