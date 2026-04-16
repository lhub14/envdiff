"""Tests for envdiff.output."""
import pytest
from pathlib import Path

from envdiff.reporter import Report
from envdiff.output import write_report


def make_report(content: str, has_diff: bool = False) -> Report:
    return Report(format="text", content=content, has_differences=has_diff)


def test_write_to_file(tmp_path):
    out = tmp_path / "report.txt"
    r = make_report("hello world")
    write_report(r, str(out))
    assert out.read_text() == "hello world"


def test_write_creates_parent_dirs(tmp_path):
    out = tmp_path / "sub" / "dir" / "report.md"
    r = make_report("# Report")
    write_report(r, str(out))
    assert out.exists()
    assert out.read_text() == "# Report"


def test_write_to_stdout(capsys):
    r = make_report("line1\nline2")
    write_report(r, output_path=None)
    captured = capsys.readouterr()
    assert "line1" in captured.out
    assert "line2" in captured.out


def test_empty_content_stdout(capsys):
    r = make_report("")
    write_report(r, output_path=None)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_write_to_file_returns_path(tmp_path):
    """write_report should return the resolved output path when writing to a file."""
    out = tmp_path / "report.txt"
    r = make_report("data")
    result = write_report(r, str(out))
    assert result == out.resolve()


def test_write_to_stdout_returns_none(capsys):
    """write_report should return None when writing to stdout."""
    r = make_report("data")
    result = write_report(r, output_path=None)
    assert result is None
