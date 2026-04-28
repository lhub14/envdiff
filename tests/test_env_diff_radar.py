"""Tests for envdiff.env_diff_radar"""
from __future__ import annotations

import pytest
from pathlib import Path

from envdiff.env_diff_radar import build_radar, RadarResult, RadarEntry, _safe_ratio


def write_env(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_safe_ratio_zero_denominator():
    assert _safe_ratio(0, 0) == 1.0


def test_safe_ratio_normal():
    assert _safe_ratio(1, 4) == 0.25


def test_build_radar_identical_files(tmp_path):
    base = write_env(tmp_path, "base.env", "A=1\nB=2\n")
    target = write_env(tmp_path, "target.env", "A=1\nB=2\n")
    result = build_radar(base, {"target": target})
    assert isinstance(result, RadarResult)
    assert len(result.entries) == 1
    entry = result.entries[0]
    assert entry.label == "target"
    assert entry.score() == 1.0


def test_build_radar_missing_key_reduces_coverage(tmp_path):
    base = write_env(tmp_path, "base.env", "A=1\nB=2\nC=3\n")
    target = write_env(tmp_path, "target.env", "A=1\nB=2\n")  # C missing
    result = build_radar(base, {"t": target})
    entry = result.entries[0]
    coverage = next(a for a in entry.axes if a.name == "coverage")
    assert coverage.value < 1.0


def test_build_radar_mismatch_reduces_consistency(tmp_path):
    base = write_env(tmp_path, "base.env", "A=1\nB=2\n")
    target = write_env(tmp_path, "target.env", "A=1\nB=DIFFERENT\n")
    result = build_radar(base, {"t": target})
    entry = result.entries[0]
    consistency = next(a for a in entry.axes if a.name == "consistency")
    assert consistency.value < 1.0


def test_build_radar_multiple_targets(tmp_path):
    base = write_env(tmp_path, "base.env", "X=1\n")
    t1 = write_env(tmp_path, "t1.env", "X=1\n")
    t2 = write_env(tmp_path, "t2.env", "X=2\n")
    result = build_radar(base, {"t1": t1, "t2": t2})
    assert len(result.entries) == 2


def test_build_radar_ignore_keys(tmp_path):
    base = write_env(tmp_path, "base.env", "A=1\nSECRET=x\n")
    target = write_env(tmp_path, "target.env", "A=1\n")  # SECRET missing but ignored
    result = build_radar(base, {"t": target}, ignore=frozenset({"SECRET"}))
    entry = result.entries[0]
    coverage = next(a for a in entry.axes if a.name == "coverage")
    assert coverage.value == 1.0


def test_radar_entry_score_average_of_axes():
    from envdiff.env_diff_radar import RadarAxis
    entry = RadarEntry(label="x", axes=[RadarAxis("a", 0.5, 1), RadarAxis("b", 1.0, 2)])
    assert entry.score() == pytest.approx(0.75)


def test_radar_entry_score_empty_axes():
    entry = RadarEntry(label="x", axes=[])
    assert entry.score() == 0.0


def test_build_radar_base_label_stored(tmp_path):
    base = write_env(tmp_path, "base.env", "K=v\n")
    target = write_env(tmp_path, "target.env", "K=v\n")
    result = build_radar(base, {"t": target})
    assert result.base_label == base
