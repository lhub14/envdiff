"""CLI command: envdiff transform"""
from __future__ import annotations

import sys
import click

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.env_transform import TransformRule, transform_env, has_changes
from envdiff.transform_formatter import format_transform_result
from envdiff.output import click_or_print


@click.command("transform")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--rule", "rules", multiple=True,
    metavar="PATTERN:OP[:ARG]",
    help="Transform rule, e.g. '*_URL:prefix:https://' or 'DEBUG:uppercase'.",
)
@click.option("--write", is_flag=True, help="Write result back to ENV_FILE.")
@click.option("--no-colour", is_flag=True)
def transform_cmd(env_file: str, rules: tuple[str, ...], write: bool, no_colour: bool) -> None:
    """Apply key/value transformations to an env file."""
    try:
        env = parse_env_file(env_file)
    except EnvParseError as exc:
        click.echo(f"Error parsing {env_file}: {exc}", err=True)
        sys.exit(2)

    parsed_rules: list[TransformRule] = []
    for raw in rules:
        parts = raw.split(":", 2)
        if len(parts) < 2:
            click.echo(f"Invalid rule: {raw!r}. Expected PATTERN:OP[:ARG]", err=True)
            sys.exit(2)
        parsed_rules.append(TransformRule(
            key_pattern=parts[0],
            operation=parts[1],
            argument=parts[2] if len(parts) == 3 else None,
        ))

    result = transform_env(env, parsed_rules)
    click_or_print(format_transform_result(result, colour=not no_colour))

    if write and has_changes(result):
        with open(env_file, "w") as fh:
            for k, v in result.transformed.items():
                fh.write(f"{k}={v}\n")
        click.echo(f"Written to {env_file}")

    sys.exit(1 if has_changes(result) else 0)
