"""CLI command: envdiff scorecard — per-key health table."""
from __future__ import annotations

import sys

import click

from envdiff.comparator import compare_envs
from envdiff.env_diff_scorecard import build_scorecard
from envdiff.lint import lint_file
from envdiff.parser import parse_env_file, EnvParseError
from envdiff.schema import load_schema, validate_against_schema, SchemaParseError
from envdiff.scorecard_formatter import format_scorecard


@click.command("scorecard")
@click.argument("base", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--schema", "schema_path", default=None, type=click.Path(), help="Optional schema file.")
@click.option("--no-colour", is_flag=True, default=False, help="Disable colour output.")
@click.option("--fail-on-issues", is_flag=True, default=False, help="Exit 1 if any key fails.")
def scorecard_cmd(
    base: str,
    target: str,
    schema_path: str | None,
    no_colour: bool,
    fail_on_issues: bool,
) -> None:
    """Show a per-key scorecard combining diff, lint, and schema checks."""
    try:
        base_env = parse_env_file(base)
        target_env = parse_env_file(target)
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(2)

    diff = compare_envs(base_env, target_env)

    lint_result = lint_file(base)

    schema_result = None
    if schema_path:
        try:
            schema = load_schema(schema_path)
            schema_result = validate_against_schema(base_env, schema)
        except SchemaParseError as exc:
            click.echo(f"Schema error: {exc}", err=True)
            sys.exit(2)

    scorecard = build_scorecard(diff, lint=lint_result, schema=schema_result)
    click.echo(format_scorecard(scorecard, colour=not no_colour))

    if fail_on_issues and scorecard.failing > 0:
        sys.exit(1)
