import json
from pathlib import Path

from scripts.append_batch_health_log import append_batch_health_log


REQUIRED_FIELDS = {
    "timestamp_utc",
    "workflow_name",
    "trigger_event",
    "github_run_id",
    "github_run_number",
    "github_sha",
    "github_ref",
    "tests_status",
    "batch_status",
    "dashboard_path",
    "dashboard_exists",
    "summary_total_count",
    "summary_pass_count",
    "summary_fail_count",
    "summary_needs_audit_count",
    "notes",
}


def _read_latest_jsonl_row(log_path: Path) -> dict:
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert lines
    return json.loads(lines[-1])


def test_append_batch_health_log_reads_summary_counts(tmp_path: Path) -> None:
    dashboard_path = tmp_path / "data/dashboard/latest_dashboard_data.json"
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.write_text(
        json.dumps(
            {
                "summary": {
                    "total_count": 6,
                    "pass_count": 4,
                    "fail_count": 1,
                    "needs_audit_count": 1,
                }
            }
        ),
        encoding="utf-8",
    )

    log_path = tmp_path / "data/logs/batch_health_log.jsonl"
    append_batch_health_log(
        tests_status="passed",
        batch_status="passed",
        dashboard_path=dashboard_path,
        log_path=log_path,
    )

    assert log_path.exists()
    row = _read_latest_jsonl_row(log_path)
    assert REQUIRED_FIELDS.issubset(set(row))
    assert row["tests_status"] == "passed"
    assert row["batch_status"] == "passed"
    assert row["dashboard_exists"] is True
    assert row["summary_total_count"] == 6
    assert row["summary_pass_count"] == 4
    assert row["summary_fail_count"] == 1
    assert row["summary_needs_audit_count"] == 1


def test_append_batch_health_log_missing_dashboard_is_safe(tmp_path: Path) -> None:
    dashboard_path = tmp_path / "data/dashboard/latest_dashboard_data.json"
    log_path = tmp_path / "data/logs/batch_health_log.jsonl"

    append_batch_health_log(
        tests_status="passed",
        batch_status="passed",
        dashboard_path=dashboard_path,
        log_path=log_path,
    )

    assert log_path.exists()
    row = _read_latest_jsonl_row(log_path)
    assert REQUIRED_FIELDS.issubset(set(row))
    assert row["dashboard_exists"] is False
    assert row["summary_total_count"] == 0
    assert row["summary_pass_count"] == 0
    assert row["summary_fail_count"] == 0
    assert row["summary_needs_audit_count"] == 0
    assert "missing" in row["notes"].lower()
