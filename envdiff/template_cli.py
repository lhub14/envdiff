"""CLI command for generating .env templates."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envdiff.parser import EnvParseError
from envdiff.template import TemplateError, template_from_file, write_template


@click.command("template")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--output", "-o", default=None, help="Output path. Defaults to stdout."
)
@click.option(
    "--include-values",
    is_flag=True,
    default=False,
    help="Include non-sensitive values in the template.",
)
@click.option(
    "--placeholder",
    default="",
    show_default=True,
    help="Value to use for redacted keys.",
)
def template_cmd(
    env_file: str,
    output: str | None,
    include_values: bool,
    placeholder: str,
) -> None:
    """Generate a .env template from ENV_FILE."""
    try:
        content = template_from_file(
            env_file,
            include_values=include_values,
            placeholder=placeholder,
        )
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(2)
    except TemplateError as exc:
        click.echo(f"Template error: {exc}", err=True)
        sys.exit(2)

    if output:
        write_template(content, output)
        click.echo(f"Template written to {output}")
    else:
        click.echo(content, nl=False)
