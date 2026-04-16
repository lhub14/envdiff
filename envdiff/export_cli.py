"""CLI command: envdiff export — dump a parsed .env file in a chosen format."""
from __future__ import annotations

import sys
import click

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.export import export_env, ExportError, SUPPORTED_FORMATS
from envdiff.redact import redact_env


@click.command("export")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--format", "fmt",
    default="dotenv",
    show_default=True,
    type=click.Choice(SUPPORTED_FORMATS),
    help="Output format.",
)
@click.option(
    "--redact", "do_redact",
    is_flag=True,
    default=False,
    help="Mask sensitive values before exporting.",
)
@click.option(
    "--output", "-o",
    default=None,
    type=click.Path(),
    help="Write output to file instead of stdout.",
)
def export_cmd(env_file: str, fmt: str, do_redact: bool, output: str | None) -> None:
    """Parse ENV_FILE and print it in the requested format."""
    try:
        env = parse_env_file(env_file)
    except EnvParseError as exc:
        click.echo(f"Error parsing {env_file}: {exc}", err=True)
        sys.exit(2)

    if do_redact:
        env = redact_env(env)

    try:
        content = export_env(env, fmt)
    except ExportError as exc:
        click.echo(str(exc), err=True)
        sys.exit(2)

    if output:
        from pathlib import Path
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(content + "\n", encoding="utf-8")
        click.echo(f"Exported to {output}")
    else:
        click.echo(content)
