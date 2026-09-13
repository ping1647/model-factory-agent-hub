from __future__ import annotations

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


def _latest_jsonl_row(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines
    return json.loads(lines[-1])


def test_append_health_log_reads_dashboard_summary(tmp_path, monkeypatch):
    dashboard_path = tmp_path / "latest_dashboard_data.json"
    log_path = tmp_path / "batch_health_log.jsonl"

    dashboard_path.write_text(
        json.dumps(
            {
                "summary": {
                    "total_count": 6,
                    "pass_count": 2,
                    "fail_count": 1,
                    "needs_audit_count": 3,
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("GITHUB_WORKFLOW", "Scheduled Batch Run")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setenv("GITHUB_RUN_NUMBER", "7")
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")

    append_batch_health_log(
        tests_status="success",
        batch_status="success",
        dashboard_path=dashboard_path,
        log_path=log_path,
    )

    assert log_path.exists()
    row = _latest_jsonl_row(log_path)

    assert REQUIRED_FIELDS.issubset(row.keys())
    assert row["workflow_name"] == "Scheduled Batch Run"
    assert row["trigger_event"] == "workflow_dispatch"
    assert row["tests_status"] == "success"
    assert row["batch_status"] == "success"
    assert row["dashboard_exists"] is True
    assert row["summary_total_count"] == 6
    assert row["summary_pass_count"] == 2
    assert row["summary_fail_count"] == 1
    assert row["summary_needs_audit_count"] == 3
    assert row["notes"] == []


def test_missing_dashboard_does_not_crash(tmp_path):
    dashboard_path = tmp_path / "missing_dashboard.json"
    log_path = tmp_path / "batch_health_log.jsonl"

    append_batch_health_log(
        tests_status="success",
        batch_status="failure",
        dashboard_path=dashboard_path,
        log_path=log_path,
    )

    row = _latest_jsonl_row(log_path)

    assert row["dashboard_exists"] is False
    assert row["summary_total_count"] is None
    assert row["summary_pass_count"] is None
    assert row["summary_fail_count"] is None
    assert row["summary_needs_audit_count"] is None
    assert "dashboard JSON not found" in row["notes"][0]


def test_malformed_dashboard_does_not_crash(tmp_path):
    dashboard_path = tmp_path / "bad_dashboard.json"
    log_path = tmp_path / "batch_health_log.jsonl"

    dashboard_path.write_text("{not valid json", encoding="utf-8")

    append_batch_health_log(
        tests_status="failure",
        batch_status="skipped",
        dashboard_path=dashboard_path,
        log_path=log_path,
    )

    row = _latest_jsonl_row(log_path)

    assert row["dashboard_exists"] is True
    assert row["summary_total_count"] is None
    assert row["summary_pass_count"] is None
    assert row["summary_fail_count"] is None
    assert row["summary_needs_audit_count"] is None
    assert "dashboard JSON malformed" in row["notes"][0]
