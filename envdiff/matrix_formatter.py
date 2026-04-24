"""Text formatter for MatrixResult."""
from __future__ import annotations

from envdiff.env_diff_matrix import MatrixResult, MatrixRow

_COL_WIDTH = 14
_KEY_WIDTH = 28


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _green(s: str) -> str:
    return f"\033[32m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _bold(s: str) -> str:
    return f"\033[1m{s}\033[0m"


def _cell(row: MatrixRow, name: str) -> str:
    c = row.cells[name]
    if not c.present:
        return _red("MISSING".center(_COL_WIDTH))
    if not row.is_uniform:
        return _yellow("MISMATCH".center(_COL_WIDTH))
    return _green("OK".center(_COL_WIDTH))


def format_matrix(result: MatrixResult, no_color: bool = False) -> str:
    if not result.rows:
        return "No keys found."

    def maybe(fn, s):  # noqa: ANN001
        return s if no_color else fn(s)

    header_parts = [_bold("KEY").ljust(_KEY_WIDTH + 9)] if not no_color else ["KEY".ljust(_KEY_WIDTH)]
    for name in result.env_names:
        header_parts.append(name.center(_COL_WIDTH))
    lines = ["  ".join(header_parts)]
    lines.append("-" * ((_KEY_WIDTH + 2) + len(result.env_names) * (_COL_WIDTH + 2)))

    for row in result.rows:
        key_col = row.key.ljust(_KEY_WIDTH)
        cols = [key_col]
        for name in result.env_names:
            cols.append(_cell(row, name) if not no_color else _cell_plain(row, name))
        lines.append("  ".join(cols))

    return "\n".join(lines)


def _cell_plain(row: MatrixRow, name: str) -> str:
    c = row.cells[name]
    if not c.present:
        return "MISSING".center(_COL_WIDTH)
    if not row.is_uniform:
        return "MISMATCH".center(_COL_WIDTH)
    return "OK".center(_COL_WIDTH)
