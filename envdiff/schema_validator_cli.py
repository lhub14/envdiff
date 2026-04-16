"""CLI integration helpers for schema validation."""
from pathlib import Path
from typing import Optional

import click

from .parser import parse_env_file, EnvParseError
from .schema import load_schema, validate_against_schema, has_violations, SchemaParseError
from .schema_formatter import format_schema_result
from .output import click_or_print


def run_schema_validation(
    env_path: str,
    schema_path: str,
    output_file: Optional[str] = None,
) -> int:
    """Validate an env file against a schema. Returns exit code."""
    try:
        env = parse_env_file(Path(env_path))
    except EnvParseError as exc:
        click.echo(f"Error parsing env file: {exc}", err=True)
        return 2

    try:
        schema = load_schema(Path(schema_path))
    except SchemaParseError as exc:
        click.echo(f"Error parsing schema file: {exc}", err=True)
        return 2

    result = validate_against_schema(env, schema)
    text = format_schema_result(result)
    click_or_print(text, output_file)
    return 1 if has_violations(result) else 0
