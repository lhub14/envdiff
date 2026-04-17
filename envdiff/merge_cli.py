"""CLI command for merging .env files."""
from __future__ import annotations
import sys
import click
from envdiff.parser import parse_env_file, EnvParseError
from envdiff.merge import merge_envs, has_conflicts
from envdiff.export import export_env, ExportError


@click.command("merge")
@click.argument("files", nargs=-1, required=True, metavar="FILE...")
@click.option("--strategy", type=click.Choice(["first", "last"]), default="first", show_default=True)
@click.option("--format", "fmt", type=click.Choice(["dotenv", "json", "shell"]), default="dotenv", show_default=True)
@click.option("--output", "-o", default=None, help="Write output to file instead of stdout.")
@click.option("--strict", is_flag=True, help="Exit with code 1 if any conflicts are detected.")
def merge_cmd(files: tuple, strategy: str, fmt: str, output: str | None, strict: bool) -> None:
    """Merge multiple .env FILES into one."""
    sources: dict = {}
    for path in files:
        try:
            sources[path] = parse_env_file(path)
        except EnvParseError as exc:
            click.echo(f"Error parsing {path}: {exc}", err=True)
            sys.exit(2)

    result = merge_envs(sources, strategy=strategy)

    if has_conflicts(result):
        for key, entries in result.conflicts.items():
            parts = ", ".join(f"{src}={val!r}" for src, val in entries)
            click.echo(f"CONFLICT {key}: {parts}", err=True)
        if strict:
            sys.exit(1)

    try:
        content = export_env(result.merged, fmt)
    except ExportError as exc:
        click.echo(f"Export error: {exc}", err=True)
        sys.exit(2)

    if output:
        from pathlib import Path
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(content)
    else:
        click.echo(content, nl=False)
