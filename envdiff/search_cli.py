"""CLI command for searching .env files."""
from __future__ import annotations

import click

from envdiff.env_search import has_matches, search_envs
from envdiff.search_formatter import format_search_result


@click.command("search")
@click.argument("pattern")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--keys/--no-keys", default=True, show_default=True, help="Search key names.")
@click.option("--values/--no-values", default=True, show_default=True, help="Search values.")
@click.option("-c", "--case-sensitive", is_flag=True, default=False, help="Case-sensitive search.")
@click.option("--no-colour", is_flag=True, default=False, help="Disable colour output.")
@click.pass_context
def search_cmd(ctx, pattern, files, keys, values, case_sensitive, no_colour):
    """Search PATTERN across one or more .env FILES."""
    labelled = {f: f for f in files}
    try:
        result = search_envs(
            labelled,
            pattern,
            search_keys=keys,
            search_values=values,
            case_sensitive=case_sensitive,
        )
    except ValueError as exc:
        click.echo(str(exc), err=True)
        ctx.exit(2)
        return

    output = format_search_result(result, colour=not no_colour)
    click.echo(output)
    ctx.exit(1 if has_matches(result) else 0)
