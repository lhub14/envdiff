"""Integration tests for the export CLI command."""
import json
from pathlib import Path
import pytest
from click.testing import CliRunner
from envdiff.export_cli import export_cmd


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("DB=postgres\nSECRET_KEY=s3cr3t\nPORT=5432\n")
    return str(p)


def test_default_dotenv_output(runner, env_file):
    result = runner.invoke(export_cmd, [env_file])
    assert result.exit_code == 0
    assert "DB=postgres" in result.output
    assert "PORT=5432" in result.output


def test_json_format(runner, env_file):
    result = runner.invoke(export_cmd, [env_file, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["PORT"] == "5432"


def test_shell_format(runner, env_file):
    result = runner.invoke(export_cmd, [env_file, "--format", "shell"])
    assert result.exit_code == 0
    assert "export DB=" in result.output


def test_redact_flag_masks_secret(runner, env_file):
    result = runner.invoke(export_cmd, [env_file, "--redact"])
    assert result.exit_code == 0
    assert "s3cr3t" not in result.output


def test_output_file(runner, env_file, tmp_path):
    out = str(tmp_path / "out" / "result.env")
    result = runner.invoke(export_cmd, [env_file, "--output", out])
    assert result.exit_code == 0
    assert Path(out).exists()
    assert "DB=postgres" in Path(out).read_text()


def test_bad_env_file_exits_2(runner, tmp_path):
    bad = tmp_path / "bad.env"
    bad.write_text("123INVALID=oops\n")
    result = runner.invoke(export_cmd, [str(bad)])
    assert result.exit_code == 2
