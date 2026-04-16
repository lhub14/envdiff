"""Tests for schema_validator_cli integration helper."""
from pathlib import Path
import pytest

from envdiff.schema_validator_cli import run_schema_validation


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_valid_env_no_violations(tmp_path):
    env = write(tmp_path, ".env", "API_KEY=abc123\nDEBUG=true\n")
    schema = write(tmp_path, "schema.env", "required:API_KEY\nrequired:DEBUG\n")
    assert run_schema_validation(env, schema) == 0


def test_missing_required_returns_1(tmp_path):
    env = write(tmp_path, ".env", "DEBUG=true\n")
    schema = write(tmp_path, "schema.env", "required:API_KEY\n")
    assert run_schema_validation(env, schema) == 1


def test_bad_env_file_returns_2(tmp_path):
    schema = write(tmp_path, "schema.env", "required:API_KEY\n")
    assert run_schema_validation("/nonexistent/.env", schema) == 2


def test_bad_schema_file_returns_2(tmp_path):
    env = write(tmp_path, ".env", "API_KEY=x\n")
    assert run_schema_validation(env, "/nonexistent/schema.env") == 2


def test_output_file_written(tmp_path):
    env = write(tmp_path, ".env", "API_KEY=abc\n")
    schema = write(tmp_path, "schema.env", "required:API_KEY\n")
    out = str(tmp_path / "out.txt")
    code = run_schema_validation(env, schema, output_file=out)
    assert code == 0
    assert Path(out).exists()
