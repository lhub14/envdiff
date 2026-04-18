"""Tests for envdiff.env_diff_patch."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.env_diff_patch import (
    EnvPatch, PatchError, PatchOperation,
    apply_patch, build_patch, load_patch,
    patch_from_json, patch_to_json, save_patch,
)


def test_build_patch_no_diff():
    env = {"A": "1", "B": "2"}
    patch = build_patch(env, env)
    assert patch.is_empty()


def test_build_patch_add():
    base = {"A": "1"}
    target = {"A": "1", "B": "2"}
    patch = build_patch(base, target)
    assert len(patch.operations) == 1
    op = patch.operations[0]
    assert op.op == "add"
    assert op.key == "B"
    assert op.new_value == "2"


def test_build_patch_remove():
    base = {"A": "1", "B": "2"}
    target = {"A": "1"}
    patch = build_patch(base, target)
    ops = {o.key: o for o in patch.operations}
    assert ops["B"].op == "remove"
    assert ops["B"].old_value == "2"


def test_build_patch_change():
    base = {"A": "old"}
    target = {"A": "new"}
    patch = build_patch(base, target)
    assert patch.operations[0].op == "change"
    assert patch.operations[0].old_value == "old"
    assert patch.operations[0].new_value == "new"


def test_apply_patch_adds_key():
    env = {"A": "1"}
    patch = EnvPatch(base_file="", target_file="",
                     operations=[PatchOperation(op="add", key="B", new_value="2")])
    result = apply_patch(env, patch)
    assert result["B"] == "2"
    assert result["A"] == "1"


def test_apply_patch_removes_key():
    env = {"A": "1", "B": "2"}
    patch = EnvPatch(base_file="", target_file="",
                     operations=[PatchOperation(op="remove", key="B", old_value="2")])
    result = apply_patch(env, patch)
    assert "B" not in result


def test_apply_patch_does_not_mutate():
    env = {"A": "1"}
    patch = EnvPatch(base_file="", target_file="",
                     operations=[PatchOperation(op="add", key="B", new_value="2")])
    apply_patch(env, patch)
    assert "B" not in env


def test_roundtrip_json():
    base = {"X": "a", "Y": "b"}
    target = {"X": "c", "Z": "d"}
    patch = build_patch(base, target, base_file="b.env", target_file="t.env")
    restored = patch_from_json(patch_to_json(patch))
    assert len(restored.operations) == len(patch.operations)
    assert restored.base_file == "b.env"


def test_save_and_load(tmp_path):
    patch = build_patch({"A": "1"}, {"A": "2"}, "a.env", "b.env")
    p = tmp_path / "my.patch"
    save_patch(patch, p)
    loaded = load_patch(p)
    assert loaded.operations[0].op == "change"


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(PatchError):
        load_patch(tmp_path / "missing.patch")


def test_patch_from_invalid_json_raises():
    with pytest.raises(PatchError):
        patch_from_json("not json at all")
