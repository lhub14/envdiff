import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envdiff.drift_cli import drift_group


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_no_drift_exit_0(runner, tmp_path):
    env = write(tmp_path, ".env", "FOO=bar\nBAR=baz\n")
    store = str(tmp_path / "store.json")
    runner.invoke(drift_group, ["check", env, "--store", store])  # save baseline first via baseline cli
    # Save baseline manually
    from envdiff.baseline import save_baseline
    save_baseline(store, "default", {"FOO": "bar", "BAR": "baz"})
    result = runner.invoke(drift_group, ["check", env, "--store", store, "--label", "default"])
    assert result.exit_code == 0


def test_drift_detected_exit_1(runner, tmp_path):
    from envdiff.baseline import save_baseline
    env = write(tmp_path, ".env", "FOO=bar\n")
    store = str(tmp_path / "store.json")
    save_baseline(store, "default", {"FOO": "bar", "MISSING": "x"})
    result = runner.invoke(drift_group, ["check", env, "--store", store])
    assert result.exit_code == 1
    assert "MISSING" in result.output


def test_json_format(runner, tmp_path):
    from envdiff.baseline import save_baseline
    env = write(tmp_path, ".env", "FOO=new\n")
    store = str(tmp_path / "store.json")
    save_baseline(store, "default", {"FOO": "old"})
    result = runner.invoke(drift_group, ["check", env, "--store", store, "--format", "json"])
    data = json.loads(result.output)
    assert data["has_drift"] is True
    assert any(c["key"] == "FOO" for c in data["changed"])


def test_missing_store_exits_2(runner, tmp_path):
    env = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(drift_group, ["check", env, "--store", str(tmp_path / "no.json")])
    assert result.exit_code == 2


def test_no_values_flag_hides_values(runner, tmp_path):
    from envdiff.baseline import save_baseline
    env = write(tmp_path, ".env", "FOO=newval\n")
    store = str(tmp_path / "store.json")
    save_baseline(store, "default", {"FOO": "oldval"})
    result = runner.invoke(drift_group, ["check", env, "--store", store, "--no-values"])
    assert "oldval" not in result.output
    assert "newval" not in result.output
