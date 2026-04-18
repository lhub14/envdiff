"""Tests for envdiff.env_clone."""
import pytest
from pathlib import Path
from envdiff.env_clone import clone_env, has_skipped


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_clone_copies_all_keys(tmp_path):
    src = write_env(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    dst = tmp_path / "out" / ".env.clone"
    result = clone_env(src, dst)
    assert set(result.keys_written) == {"FOO", "BAZ"}
    assert result.keys_skipped == []
    assert dst.exists()


def test_clone_include_filter(tmp_path):
    src = write_env(tmp_path, ".env", "FOO=bar\nBAZ=qux\nSECRET=x\n")
    dst = tmp_path / ".env.out"
    result = clone_env(src, dst, include=["FOO", "SECRET"])
    assert "BAZ" in result.keys_skipped
    assert "FOO" in result.keys_written
    content = dst.read_text()
    assert "FOO" in content
    assert "BAZ" not in content


def test_clone_exclude_filter(tmp_path):
    src = write_env(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    dst = tmp_path / ".env.out"
    result = clone_env(src, dst, exclude=["BAZ"])
    assert "BAZ" in result.keys_skipped
    assert "FOO" in result.keys_written


def test_clone_redact_sensitive(tmp_path):
    src = write_env(tmp_path, ".env", "API_KEY=supersecret\nHOST=localhost\n")
    dst = tmp_path / ".env.out"
    result = clone_env(src, dst, redact=True)
    assert "API_KEY" in result.redacted_keys
    assert "HOST" not in result.redacted_keys
    content = dst.read_text()
    assert "supersecret" not in content
    assert "localhost" in content


def test_dry_run_does_not_write(tmp_path):
    src = write_env(tmp_path, ".env", "FOO=bar\n")
    dst = tmp_path / ".env.clone"
    result = clone_env(src, dst, dry_run=True)
    assert not dst.exists()
    assert "FOO" in result.keys_written


def test_has_skipped_true_false(tmp_path):
    src = write_env(tmp_path, ".env", "A=1\nB=2\n")
    dst = tmp_path / "out.env"
    r_all = clone_env(src, dst)
    assert not has_skipped(r_all)
    r_excl = clone_env(src, dst, exclude=["A"])
    assert has_skipped(r_excl)


def test_creates_parent_directories(tmp_path):
    src = write_env(tmp_path, ".env", "X=1\n")
    dst = tmp_path / "deep" / "nested" / ".env"
    clone_env(src, dst)
    assert dst.exists()
