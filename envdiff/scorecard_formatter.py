"""Text formatter for ScorecardResult."""
from __future__ import annotations

from envdiff.env_diff_scorecard import ScorecardResult


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def format_scorecard(result: ScorecardResult, *, colour: bool = True) -> str:
    if not result.rows:
        msg = "No keys to score."
        return _green(msg) if colour else msg

    lines: list[str] = []
    header = f"{'KEY':<30} {'BASE':>5} {'TARGET':>6} {'MATCH':>5} {'LINT':>5} {'SCHEMA':>6} {'OK':>4}"
    lines.append(_bold(header) if colour else header)
    lines.append("-" * len(header))

    for row in result.rows:
        def _tick(val: bool) -> str:
            sym = "yes" if val else "no "
            if not colour:
                return sym
            return _green(sym) if val else _red(sym)

        lint_count = str(len(row.lint_warnings)) if row.lint_warnings else "-"
        schema_count = str(len(row.schema_violations)) if row.schema_violations else "-"

        if colour and (row.lint_warnings or row.schema_violations):
            lint_count = _yellow(lint_count)
            schema_count = _yellow(schema_count)

        ok_sym = (_green("✓") if colour else "pass") if row.ok else (_red("✗") if colour else "fail")

        lines.append(
            f"{row.key:<30} {_tick(row.in_base):>5} {_tick(row.in_target):>6} "
            f"{_tick(row.values_match):>5} {lint_count:>5} {schema_count:>6} {ok_sym:>4}"
        )

    lines.append("-" * len(header))
    summary = f"Total: {result.total}  Passing: {result.passing}  Failing: {result.failing}"
    lines.append(_bold(summary) if colour else summary)
    return "\n".join(lines)
