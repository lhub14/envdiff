import click
import sys
import json

from envdiff.baseline import load_baseline, BaselineError
from envdiff.drift import detect_drift, has_drift
from envdiff.drift_formatter import format_drift


@click.group(name="drift")
def drift_group():
    """Detect drift between a saved baseline and a live .env file."""


@drift_group.command(name="check")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--label", default="default", show_default=True, help="Baseline label to compare against.")
@click.option("--store", default=".envdiff_baselines.json", show_default=True, help="Path to baseline store.")
@click.option("--format", "fmt", type=click.Choice(["text", "json"]), default="text", show_default=True)
@click.option("--no-values", is_flag=True, default=False, help="Hide values in output.")
def check_cmd(env_file, label, store, fmt, no_values):
    """Compare ENV_FILE against a stored baseline."""
    try:
        baseline = load_baseline(store, label)
    except BaselineError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(2)

    from envdiff.parser import parse_env_file, EnvParseError
    try:
        live = parse_env_file(env_file)
    except EnvParseError as exc:
        click.echo(f"Error parsing {env_file}: {exc}", err=True)
        sys.exit(2)

    result = detect_drift(baseline.keys, live)

    if fmt == "json":
        click.echo(json.dumps({
            "label": label,
            "added": result.added,
            "removed": result.removed,
            "changed": [
                {"key": k, "baseline": b, "live": l}
                for k, b, l in result.changed
            ],
            "has_drift": has_drift(result),
        }, indent=2))
    else:
        click.echo(format_drift(result, show_values=not no_values))

    sys.exit(1 if has_drift(result) else 0)
