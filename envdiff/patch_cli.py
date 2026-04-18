"""CLI commands for env diff patch: generate and apply."""
from __future__ import annotations

from pathlib import Path

import click

from envdiff.env_diff_patch import (
    PatchError, apply_patch, build_patch, load_patch, save_patch,
)
from envdiff.parser import EnvParseError, parse_env_file
from envdiff.export import _to_dotenv


@click.group("patch")
def patch_group() -> None:
    """Generate or apply .env patch files."""


@patch_group.command("generate")
@click.argument("base", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Write patch to file (default: stdout)")
def generate_cmd(base: str, target: str, output: str | None) -> None:
    """Generate a patch from BASE to TARGET."""
    try:
        base_env = parse_env_file(Path(base))
        target_env = parse_env_file(Path(target))
    except EnvParseError as exc:
        raise click.ClickException(str(exc))

    from envdiff.env_diff_patch import patch_to_json
    patch = build_patch(base_env, target_env, base_file=base, target_file=target)
    content = patch_to_json(patch)

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(content, encoding="utf-8")
        click.echo(f"Patch written to {output}")
    else:
        click.echo(content)


@patch_group.command("apply")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("patch_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Write patched env to file (default: stdout)")
def apply_cmd(env_file: str, patch_file: str, output: str | None) -> None:
    """Apply PATCH_FILE to ENV_FILE."""
    try:
        env = parse_env_file(Path(env_file))
    except EnvParseError as exc:
        raise click.ClickException(str(exc))

    try:
        patch = load_patch(Path(patch_file))
    except PatchError as exc:
        raise click.ClickException(str(exc))

    result = apply_patch(env, patch)
    lines = [f"{k}={v}" for k, v in sorted(result.items())]
    content = "\n".join(lines) + "\n"

    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(content, encoding="utf-8")
        click.echo(f"Patched env written to {output}")
    else:
        click.echo(content, nl=False)
