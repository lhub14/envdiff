"""Tests for envdiff.env_reorder."""
from pathlib import Path

import pytest

from envdiff.env_reorder import reorder_env, reorder_env_file, write_reordered


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_already_ordered_not_changed():
    source = {"A": "1", "B": "2", "C": "3"}
    result = reorder_env(source, ["A", "B", "C"])
    assert not result.changed
    assert result.moved_keys == []
    assert result.appended_keys == []


def test_reorder_detected_as_changed():
    source = {"B": "2", "A": "1", "C": "3"}
    result = reorder_env(source, ["A", "B", "C"])
    assert result.changed
    assert result.reordered_lines == ["A=1", "B=2", "C=3"]


def test_keys_not_in_reference_appended():
    source = {"A": "1", "Z": "99", "B": "2"}
    result = reorder_env(source, ["A", "B"])
    assert result.appended_keys == ["Z"]
    assert result.reordered_lines[-1] == "Z=99"


def test_reference_keys_missing_from_source_skipped():
    source = {"A": "1", "C": "3"}
    result = reorder_env(source, ["A", "B", "C"])
    assert result.reordered_lines == ["A=1", "C=3"]
    assert result.appended_keys == []


def test_value_with_space_quoted():
    source = {"KEY": "hello world"}
    result = reorder_env(source, ["KEY"])
    assert result.reordered_lines == ['KEY="hello world"']


def test_empty_value_quoted():
    source = {"EMPTY": ""}
    result = reorder_env(source, ["EMPTY"])
    assert result.reordered_lines == ['EMPTY=""']


def test_reorder_env_file(tmp_path: Path):
    src = write_env(tmp_path, "src.env", "B=2\nA=1\n")
    ref = write_env(tmp_path, "ref.env", "A=x\nB=x\n")
    result = reorder_env_file(src, ref)
    assert result.changed
    assert result.reordered_lines == ["A=1", "B=2"]


def test_write_reordered(tmp_path: Path):
    src = write_env(tmp_path, "src.env", "B=2\nA=1\n")
    ref = write_env(tmp_path, "ref.env", "A=x\nB=x\n")
    result = reorder_env_file(src, ref)
    out = tmp_path / "out.env"
    write_reordered(result, out)
    content = out.read_text(encoding="utf-8")
    assert content == "A=1\nB=2\n"


def test_write_creates_parent_dirs(tmp_path: Path):
    src = write_env(tmp_path, "src.env", "A=1\n")
    ref = write_env(tmp_path, "ref.env", "A=x\n")
    result = reorder_env_file(src, ref)
    out = tmp_path / "nested" / "dir" / "out.env"
    write_reordered(result, out)
    assert out.exists()
