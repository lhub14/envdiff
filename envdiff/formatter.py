"""Format DiffResult for terminal output."""

from typing import Optional

from envdiff.comparator import DiffResult

TRY_COLORS = True

try:
    from colorama import Fore, Style, init as colorama_init

    colorama_init(autoreset=True)
except ImportError:  # pragma: no cover
    TRY_COLORS = False


def _red(text: str) -> str:
    if TRY_COLORS:
        return f"{Fore.RED}{text}{Style.RESET_ALL}"
    return text


def _yellow(text: str) -> str:
    if TRY_COLORS:
        return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
    return text


def _green(text: str) -> str:
    if TRY_COLORS:
        return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
    return text


def format_diff(result: DiffResult, show_values: bool = False) -> str:
    """Render a DiffResult as a human-readable string."""
    lines = [
        f"Comparing {result.base_name!r} (base) vs {result.target_name!r} (target)",
        "-" * 60,
    ]

    if not result.has_differences:
        lines.append(_green("No differences found."))
        return "\n".join(lines)

    if result.missing_in_target:
        lines.append(_red(f"Missing in {result.target_name} ({len(result.missing_in_target)}):"))
        for key in result.missing_in_target:
            lines.append(f"  - {key}")

    if result.missing_in_base:
        lines.append(_yellow(f"Extra in {result.target_name} ({len(result.missing_in_base)}):"))
        for key in result.missing_in_base:
            lines.append(f"  + {key}")

    if result.value_mismatches:
        lines.append(_yellow(f"Value mismatches ({len(result.value_mismatches)}):"))
        for key, (base_val, target_val) in result.value_mismatches.items():
            if show_values:
                lines.append(f"  ~ {key}: {base_val!r} -> {target_val!r}")
            else:
                lines.append(f"  ~ {key}")

    return "\n".join(lines)
