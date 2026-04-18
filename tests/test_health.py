"""Tests for envdiff.health."""
from envdiff.health import check_health, format_health, HealthReport
from envdiff.score import ScoreResult
from envdiff.lint import LintResult, LintIssue


def _score(s: int, grade: str = "A") -> ScoreResult:
    return ScoreResult(score=s, grade=grade, missing=0, mismatched=0, total=10)


def _lint(issues: list[LintIssue] | None = None) -> LintResult:
    return LintResult(issues=issues or [])


def test_all_good_is_pass():
    report = check_health(_score(100, "A"), _lint())
    assert report.status == "pass"
    assert report.error_count == 0
    assert report.warning_count == 0
    assert report.reasons == []


def test_low_score_is_fail():
    report = check_health(_score(50, "F"), _lint(), score_threshold=80)
    assert report.status == "fail"
    assert any("50" in r for r in report.reasons)


def test_lint_error_is_fail():
    issues = [LintIssue(key="BAD KEY", message="invalid key", severity="error")]
    report = check_health(_score(95, "A"), _lint(issues))
    assert report.status == "fail"
    assert report.error_count == 1


def test_lint_warning_only_is_warn():
    issues = [LintIssue(key="lower", message="lowercase key", severity="warning")]
    report = check_health(_score(95, "A"), _lint(issues))
    assert report.status == "warn"
    assert report.warning_count == 1
    assert report.error_count == 0


def test_custom_threshold():
    report = check_health(_score(75, "C"), _lint(), score_threshold=70)
    assert report.status == "pass"


def test_format_pass():
    report = HealthReport(status="pass", score=100, grade="A",
                          error_count=0, warning_count=0, reasons=[])
    out = format_health(report)
    assert "PASS" in out
    assert "100" in out


def test_format_fail_shows_reasons():
    report = HealthReport(status="fail", score=40, grade="F",
                          error_count=1, warning_count=0,
                          reasons=["1 lint error(s) found", "score 40 is below threshold 80"])
    out = format_health(report)
    assert "FAIL" in out
    assert "lint error" in out
    assert "threshold" in out


def test_format_warn_icon():
    report = HealthReport(status="warn", score=90, grade="A",
                          error_count=0, warning_count=2,
                          reasons=["2 lint warning(s) found"])
    out = format_health(report)
    assert "WARN" in out
    assert "!" in out
