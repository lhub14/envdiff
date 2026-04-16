"""Tests for envdiff.template."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.template import generate_template, template_from_file, write_template


def write_env(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_generate_template_all_redacted():
    env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp"}
    result = generate_template(env)
    assert "DB_PASSWORD=" in result
    assert "APP_NAME=" in result
    assert "secret" not in result
    assert "myapp" not in result


def test_generate_template_include_values_skips_sensitive():
    env = {"DB_PASSWORD": "secret", "APP_NAME": "myapp"}
    result = generate_template(env, include_values=True)
    assert "APP_NAME=myapp" in result
    assert "secret" not in result


def test_generate_template_placeholder():
    env = {"FOO": "bar"}
    result = generate_template(env, placeholder="CHANGE_ME")
    assert "FOO=CHANGE_ME" in result


def test_generate_template_empty_env():
    assert generate_template({}) == ""


def test_generate_template_sorted_keys():
    env = {"Z_KEY": "1", "A_KEY": "2"}
    result = generate_template(env)
    lines = [l for l in result.splitlines() if l]
    assert lines[0].startswith("A_KEY")
    assert lines[1].startswith("Z_KEY")


def test_template_from_file(tmp_path: Path):
    p = write_env(tmp_path, ".env", "FOO=bar\nSECRET_KEY=abc\n")
    result = template_from_file(p)
    assert "FOO=" in result
    assert "bar" not in result


def test_write_template_creates_parents(tmp_path: Path):
    dest = tmp_path / "nested" / "dir" / ".env.template"
    write_template("FOO=\n", dest)
    assert dest.exists()
    assert dest.read_text() == "FOO=\n"
