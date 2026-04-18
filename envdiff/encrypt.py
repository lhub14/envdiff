"""Encrypt and decrypt .env file values using Fernet symmetric encryption."""
from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Dict

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore


class EncryptError(Exception):
    """Raised when encryption/decryption fails."""


def _require_fernet() -> None:
    if Fernet is None:
        raise EncryptError("cryptography package is required: pip install cryptography")


def generate_key() -> str:
    """Return a new base64-encoded Fernet key as a string."""
    _require_fernet()
    return Fernet.generate_key().decode()


def encrypt_env(env: Dict[str, str], key: str) -> Dict[str, str]:
    """Return a new dict with all values encrypted."""
    _require_fernet()
    f = Fernet(key.encode())
    return {k: f.encrypt(v.encode()).decode() for k, v in env.items()}


def decrypt_env(env: Dict[str, str], key: str) -> Dict[str, str]:
    """Return a new dict with all values decrypted."""
    _require_fernet()
    f = Fernet(key.encode())
    result: Dict[str, str] = {}
    for k, v in env.items():
        try:
            result[k] = f.decrypt(v.encode()).decode()
        except InvalidToken as exc:
            raise EncryptError(f"Failed to decrypt key '{k}': invalid token") from exc
    return result


def save_encrypted(env: Dict[str, str], key: str, path: Path) -> None:
    """Encrypt env and write JSON to path."""
    encrypted = encrypt_env(env, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(encrypted, indent=2))


def load_encrypted(key: str, path: Path) -> Dict[str, str]:
    """Load encrypted JSON from path and return decrypted env dict."""
    if not path.exists():
        raise EncryptError(f"Encrypted file not found: {path}")
    try:
        encrypted = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise EncryptError(f"Invalid JSON in encrypted file: {exc}") from exc
    return decrypt_env(encrypted, key)
