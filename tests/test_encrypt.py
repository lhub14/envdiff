"""Tests for envdiff.encrypt."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

pytest.importorskip("cryptography")

from envdiff.encrypt import (
    generate_key,
    encrypt_env,
    decrypt_env,
    save_encrypted,
    load_encrypted,
    EncryptError,
)


@pytest.fixture()
def key() -> str:
    return generate_key()


def test_generate_key_returns_string(key):
    assert isinstance(key, str)
    assert len(key) > 0


def test_encrypt_decrypt_roundtrip(key):
    env = {"DB_HOST": "localhost", "SECRET": "hunter2"}
    encrypted = encrypt_env(env, key)
    assert encrypted["DB_HOST"] != "localhost"
    assert decrypt_env(encrypted, key) == env


def test_encrypt_does_not_mutate(key):
    env = {"A": "1"}
    encrypted = encrypt_env(env, key)
    assert env == {"A": "1"}


def test_decrypt_wrong_key():
    key1 = generate_key()
    key2 = generate_key()
    encrypted = encrypt_env({"X": "val"}, key1)
    with pytest.raises(EncryptError, match="invalid token"):
        decrypt_env(encrypted, key2)


def test_save_and_load_encrypted(tmp_path, key):
    env = {"FOO": "bar", "BAZ": "qux"}
    out = tmp_path / "secrets" / "env.enc"
    save_encrypted(env, key, out)
    assert out.exists()
    loaded = load_encrypted(key, out)
    assert loaded == env


def test_save_creates_parent_dirs(tmp_path, key):
    out = tmp_path / "a" / "b" / "c.enc"
    save_encrypted({"K": "v"}, key, out)
    assert out.exists()


def test_load_missing_file_raises(tmp_path, key):
    with pytest.raises(EncryptError, match="not found"):
        load_encrypted(key, tmp_path / "missing.enc")


def test_load_invalid_json_raises(tmp_path, key):
    bad = tmp_path / "bad.enc"
    bad.write_text("not json")
    with pytest.raises(EncryptError, match="Invalid JSON"):
        load_encrypted(key, bad)


def test_saved_file_is_valid_json(tmp_path, key):
    save_encrypted({"A": "1"}, key, tmp_path / "e.enc")
    data = json.loads((tmp_path / "e.enc").read_text())
    assert "A" in data
