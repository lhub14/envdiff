"""Tests for envdiff.baseline module."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.baseline import (
    BaselineError,
    diff_against_baseline,
    list_baselines,
    load_baseline,
    save_baseline,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "baselines.json"


def test_save_and_load(store: Path) -> None:
    env = {"KEY": "value", "PORT": "8080"}
    save_baseline("prod", env, store, created_at="2024-01-01T00:00:00")
    bl = load_baseline("prod", store)
    assert bl.label == "prod"
    assert bl.env == env
    assert bl.created_at == "2024-01-01T00:00:00"


def test_save_multiple_labels(store: Path) -> None:
    save_baseline("prod", {"A": "1"}, store)
    save_baseline("staging", {"A": "2"}, store)
    assert set(list_baselines(store)) == {"prod", "staging"}


def test_save_overwrites_existing_label(store: Path) -> None:
    """Saving a baseline with an existing label should update it in place."""
    save_baseline("prod", {"A": "1"}, store)
    save_baseline("prod", {"A": "2"}, store)
    bl = load_baseline("prod", store)
    assert bl.env == {"A": "2"}
    assert list_baselines(store) == ["prod"]


def test_load_missing_store_raises(store: Path) -> None:
    with pytest.raises(BaselineError, match="No baseline store"):
        load_baseline("prod", store)


def test_load_missing_label_raises(store: Path) -> None:
    save_baseline("prod", {}, store)
    with pytest.raises(BaselineError, match="not found"):
        load_baseline("staging", store)


def test_corrupt_store_raises(store: Path) -> None:
    store.write_text("not json")
    with pytest.raises(BaselineError, match="Corrupt"):
        load_baseline("prod", store)


def test_diff_no_differences(store: Path) -> None:
    env = {"A": "1", "B": "2"}
    save_baseline("base", env, store)
    result = diff_against_baseline("base", env, store)
    assert not result.missing_in_target
    assert not result.missing_in_base
    assert not result.mismatched


def test_diff_detects_missing(store: Path) -> None:
    save_baseline("base", {"A": "1", "B": "2"}, store)
    result = diff_against_baseline("base", {"A": "1"}, store)
    assert "B" in result.missing_in_target


def test_diff_detects_extra_in_target(store: Path) -> None:
    """Keys present in target but absent in base should appear in missing_in_base."""
    save_baseline("base", {"A": "1"}, store)
    result = diff_against_baseline("base", {"A": "1", "B": "2"}, store)
    assert "B" in result.missing_in_base


def test_diff_detects_mismatch(store: Path) -> None:
    save_baseline("base", {"A": "old"}, store)
    result = diff_against_baseline("base", {"A": "new"}, store)
    assert "A" in result.mismatched


def test_list_baselines_empty(store: Path) -> None:
    assert list_baselines(store) == []
