"""Tests for envdiff.encrypt_cli."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

pytest.importorskip("cryptography")

from envdiff.encrypt_cli import encrypt_group
from envdiff.encrypt import generate_key


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def key():
    return generate_key()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_keygen_prints_key(runner):
    result = runner.invoke(encrypt_group, ["keygen"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 10


def test_lock_creates_encrypted_file(runner, tmp_path, key):
    env_file = write(tmp_path, ".env", "SECRET=hunter2\nHOST=localhost\n")
    out = tmp_path / "env.enc"
    result = runner.invoke(encrypt_group, ["lock", str(env_file), str(out), "--key", key])
    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert "SECRET" in data
    assert data["SECRET"] != "hunter2"


def test_unlock_prints_to_stdout(runner, tmp_path, key):
    env_file = write(tmp_path, ".env", "FOO=bar\n")
    out = tmp_path / "env.enc"
    runner.invoke(encrypt_group, ["lock", str(env_file), str(out), "--key", key])
    result = runner.invoke(encrypt_group, ["unlock", str(out), "--key", key])
    assert result.exit_code == 0
    assert "FOO" in result.output


def test_unlock_to_file(runner, tmp_path, key):
    env_file = write(tmp_path, ".env", "BAR=baz\n")
    enc = tmp_path / "env.enc"
    dec = tmp_path / "decrypted.env"
    runner.invoke(encrypt_group, ["lock", str(env_file), str(enc), "--key", key])
    result = runner.invoke(encrypt_group, ["unlock", str(enc), "--key", key, "--output", str(dec)])
    assert result.exit_code == 0
    assert dec.exists()
    assert "BAR" in dec.read_text()


def test_lock_bad_env_file_exits_1(runner, tmp_path, key):
    bad = write(tmp_path, "bad.env", "123INVALID=value\n")
    out = tmp_path / "out.enc"
    result = runner.invoke(encrypt_group, ["lock", str(bad), str(out), "--key", key])
    assert result.exit_code == 1


def test_unlock_wrong_key_exits_1(runner, tmp_path, key):
    env_file = write(tmp_path, ".env", "X=1\n")
    enc = tmp_path / "env.enc"
    runner.invoke(encrypt_group, ["lock", str(env_file), str(enc), "--key", key])
    wrong_key = generate_key()
    result = runner.invoke(encrypt_group, ["unlock", str(enc), "--key", wrong_key])
    assert result.exit_code == 1
