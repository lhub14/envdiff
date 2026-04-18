"""Generate and apply patch files to sync one .env to another."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class PatchError(Exception):
    pass


@dataclass
class PatchOperation:
    op: str  # "add" | "remove" | "change"
    key: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None


@dataclass
class EnvPatch:
    base_file: str
    target_file: str
    operations: List[PatchOperation] = field(default_factory=list)

    def is_empty(self) -> bool:
        return len(self.operations) == 0


def build_patch(base: Dict[str, str], target: Dict[str, str],
                base_file: str = "", target_file: str = "") -> EnvPatch:
    ops: List[PatchOperation] = []
    all_keys = set(base) | set(target)
    for key in sorted(all_keys):
        if key in base and key not in target:
            ops.append(PatchOperation(op="remove", key=key, old_value=base[key]))
        elif key not in base and key in target:
            ops.append(PatchOperation(op="add", key=key, new_value=target[key]))
        elif base[key] != target[key]:
            ops.append(PatchOperation(op="change", key=key,
                                      old_value=base[key], new_value=target[key]))
    return EnvPatch(base_file=base_file, target_file=target_file, operations=ops)


def apply_patch(env: Dict[str, str], patch: EnvPatch) -> Dict[str, str]:
    result = dict(env)
    for op in patch.operations:
        if op.op == "add":
            result[op.key] = op.new_value or ""
        elif op.op == "remove":
            result.pop(op.key, None)
        elif op.op == "change":
            result[op.key] = op.new_value or ""
    return result


def patch_to_json(patch: EnvPatch) -> str:
    data = {
        "base_file": patch.base_file,
        "target_file": patch.target_file,
        "operations": [
            {k: v for k, v in vars(op).items() if v is not None}
            for op in patch.operations
        ],
    }
    return json.dumps(data, indent=2)


def patch_from_json(text: str) -> EnvPatch:
    try:
        data = json.loads(text)
        ops = [PatchOperation(**o) for o in data.get("operations", [])]
        return EnvPatch(base_file=data["base_file"],
                        target_file=data["target_file"],
                        operations=ops)
    except Exception as exc:
        raise PatchError(f"Invalid patch file: {exc}") from exc


def save_patch(patch: EnvPatch, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(patch_to_json(patch), encoding="utf-8")


def load_patch(path: Path) -> EnvPatch:
    if not path.exists():
        raise PatchError(f"Patch file not found: {path}")
    return patch_from_json(path.read_text(encoding="utf-8"))
