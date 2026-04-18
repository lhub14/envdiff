"""CLI commands for encrypting and decrypting .env files."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envdiff.encrypt import EncryptError, generate_key, save_encrypted, load_encrypted
from envdiff.parser import parse_env_file, EnvParseError
from envdiff.export import _to_dotenv


@click.group("encrypt")
def encrypt_group() -> None:
    """Encrypt and decrypt .env files."""


@encrypt_group.command("keygen")
def keygen_cmd() -> None:
    """Generate a new encryption key and print it."""
    try:
        click.echo(generate_key())
    except EncryptError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@encrypt_group.command("lock")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--key", required=True, envvar="ENVDIFF_KEY", help="Fernet key string.")
def lock_cmd(env_file: str, output: str, key: str) -> None:
    """Encrypt ENV_FILE and write to OUTPUT."""
    try:
        env = parse_env_file(Path(env_file))
        save_encrypted(env, key, Path(output))
        click.echo(f"Encrypted {env_file} -> {output}")
    except (EnvParseError, EncryptError) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@encrypt_group.command("unlock")
@click.argument("encrypted_file", type=click.Path(exists=True))
@click.option("--key", required=True, envvar="ENVDIFF_KEY", help="Fernet key string.")
@click.option("--output", "-o", default=None, type=click.Path(), help="Write to file instead of stdout.")
def unlock_cmd(encrypted_file: str, key: str, output: str | None) -> None:
    """Decrypt ENCRYPTED_FILE and print or write the .env contents."""
    try:
        env = load_encrypted(key, Path(encrypted_file))
        content = _to_dotenv(env)
        if output:
            Path(output).write_text(content)
            click.echo(f"Decrypted -> {output}")
        else:
            click.echo(content, nl=False)
    except EncryptError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
