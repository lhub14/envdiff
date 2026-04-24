"""CLI command: envdiff report-card — produce a graded summary for a .env file."""
from __future__ import annotations

import json
import sys

import click

from envdiff.parser import parse_env_file, EnvParseError
from envdiff.comparator import compare_envs
from envdiff.score import compute_score
from envdiff.lint import lint_env
from envdiff.drift import detect_drift
from envdiff.health import check_health
from envdiff.env_diff_report_card import build_report_card, report_card_to_json
from envdiff.report_card_formatter import format_report_card


@click.command("report-card")
@click.argument("base", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--baseline", "baseline_path", default=None, help="Baseline store for drift check.")
@click.option("--label", default="", help="Optional label shown in the report.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
@click.option("--no-colour", is_flag=True, default=False)
def report_card_cmd(base, target, baseline_path, label, fmt, no_colour):
    """Produce a graded report card comparing BASE to TARGET."""
    try:
        base_env = parse_env_file(base)
        target_env = parse_env_file(target)
    except EnvParseError as exc:
        click.echo(f"Parse error: {exc}", err=True)
        sys.exit(2)

    diff = compare_envs(base_env, target_env)
    score = compute_score(diff)
    lint = lint_env(base)
    health = check_health(score, lint)

    drift = None
    if baseline_path:
        from envdiff.baseline import load_baseline, BaselineError
        try:
            bl = load_baseline(baseline_path, label or "default")
            drift = detect_drift(bl, target_env)
        except BaselineError:
            click.echo("Warning: baseline not found, skipping drift check.", err=True)

    card = build_report_card(score, lint, drift, health, label=label)

    if fmt == "json":
        click.echo(json.dumps(report_card_to_json(card), indent=2))
    else:
        click.echo(format_report_card(card, colour=not no_colour))

    sys.exit(0 if card.passed else 1)
