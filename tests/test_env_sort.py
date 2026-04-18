"""Tests for envdiff.env_sort."""
from pathlib import Path

import pytest

from envdiff.env_sort import sort_env_file, write_sorted


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


def test_already_sorted_not_changed(tmp_path):
    p = write_env(tmp_path, ".env", "ALPHA=1\nBETA=2\nZETA=3\n")
    result = sort_env_file(p)
    assert not result.changed
    assert result.sorted_order == ["ALPHA", "BETA", "ZETA"]


def test_unsorted_detected_as_changed(tmp_path):
    p = write_env(tmp_path, ".env", "ZETA=3\nALPHA=1\nBETA=2\n")
    result = sort_env_file(p)
    assert result.changed
    assert result.sorted_order == ["ALPHA", "BETA", "ZETA"]


def test_reverse_sort(tmp_path):
    p = write_env(tmp_path, ".env", "ALPHA=1\nBETA=2\nZETA=3\n")
    result = sort_env_file(p, reverse=True)
    assert result.sorted_order == ["ZETA", "BETA", "ALPHA"]


def test_output_lines_contain_key_value(tmp_path):
    p = write_env(tmp_path, ".env", "B=hello world\nA=simple\n")
    result = sort_env_file(p)
    assert result.output_lines[0] == 'A=simple'
    assert result.output_lines[1] == 'B="hello world"'


def test_group_prefix_clusters_keys(tmp_path):
    p = write_env(tmp_path, ".env", "DB_PORT=5432\nAPP_NAME=x\nDB_HOST=localhost\nAPP_ENV=prod\n")
    result = sort_env_file(p, group_prefix=True)
    prefixes = [k.split("_")[0] for k in result.sorted_order]
    # All APP keys come before DB keys (alphabetical prefix order)
    app_indices = [i for i, k in enumerate(result.sorted_order) if k.startswith("APP")]
    db_indices = [i for i, k in enumerate(result.sorted_order) if k.startswith("DB")]
    assert max(app_indices) < min(db_indices)


def test_write_sorted_creates_file(tmp_path):
    p = write_env(tmp_path, ".env", "Z=last\nA=first\n")
    result = sort_env_file(p)
    dest = tmp_path / "sorted" / ".env.sorted"
    write_sorted(result, dest)
    content = dest.read_text(encoding="utf-8")
    assert content.startswith("A=first\n")
    assert "Z=last" in content


def test_empty_env_file(tmp_path):
    p = write_env(tmp_path, ".env", "# just a comment\n")
    result = sort_env_file(p)
    assert result.sorted_order == []
    assert not result.changed
    assert result.output_lines == []
