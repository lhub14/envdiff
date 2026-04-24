"""Formatter for contextual diff output."""
from __future__ import annotations

from typing import List, Tuple

from envdiff.env_diff_context import ContextBlock, ContextDiffResult


def _dim(s: str) -> str:
    return f"\033[2m{s}\033[0m"


def _red(s: str) -> str:
    return f"\033[31m{s}\033[0m"


def _yellow(s: str) -> str:
    return f"\033[33m{s}\033[0m"


def _cyan(s: str) -> str:
    return f"\033[36m{s}\033[0m"


def _label(change_type: str) -> str:
    labels = {
        "missing_in_target": _red("[-] missing in target"),
        "missing_in_base": _cyan("[+] missing in base"),
        "mismatch": _yellow("[~] mismatch"),
    }
    return labels.get(change_type, change_type)


def _fmt_ctx_line(key: str, value: str) -> str:
    return _dim(f"    {key}={value}")


def _fmt_block(block: ContextBlock) -> List[str]:
    lines: List[str] = []
    if block.before:
        lines.append(_dim("  ..."))
    for k, v in block.before:
        lines.append(_fmt_ctx_line(k, v))

    header = f"  {block.key}  {_label(block.change_type)}"
    if block.change_type == "mismatch":
        header += f"  base={block.base_value!r}  target={block.target_value!r}"
    elif block.change_type == "missing_in_target":
        header += f"  value={block.base_value!r}"
    elif block.change_type == "missing_in_base":
        header += f"  value={block.target_value!r}"
    lines.append(header)

    for k, v in block.after:
        lines.append(_fmt_ctx_line(k, v))
    if block.after:
        lines.append(_dim("  ..."))
    return lines


def format_context_diff(result: ContextDiffResult, no_color: bool = False) -> str:
    if result.is_empty():
        return "No differences found."
    parts: List[str] = []
    for block in result.blocks:
        parts.extend(_fmt_block(block))
        parts.append("")
    text = "\n".join(parts).rstrip()
    if no_color:
        import re
        text = re.sub(r"\033\[[0-9;]*m", "", text)
    return text
