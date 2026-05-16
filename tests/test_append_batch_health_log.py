import json
from pathlib import Path

from scripts import append_batch_health_log as module


def test_append_batch_health_log_with_dashboard_summary(tmp_path, monkeypatch):
    dashboard_path = tmp_path / "latest_dashboard_data.json"
    log_path = tmp_path / "batch_health_log.jsonl"

    dashboard_payload = {
        "summary": {
            "total_count": 12,
            "pass_count": 8,
            "fail_count": 2,
            "needs_audit_count": 2,
        }
    }
    dashboard_path.write_text(json.dumps(dashboard_payload), encoding="utf-8")

    monkeypatch.setattr(module, "DEFAULT_DASHBOARD_PATH", dashboard_path)
    monkeypatch.setattr(module, "DEFAULT_LOG_PATH", log_path)

    record = module.append_batch_health_log(tests_status="passed", batch_status="passed")

    assert log_path.exists()
    assert record["tests_status"] == "passed"
    assert record["batch_status"] == "passed"
    assert record["summary_total_count"] == 12
    assert record["summary_pass_count"] == 8
    assert record["summary_fail_count"] == 2
    assert record["summary_needs_audit_count"] == 2

    row = json.loads(log_path.read_text(encoding="utf-8").strip())
    required_fields = {
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
    assert required_fields.issubset(row.keys())


def test_append_batch_health_log_missing_dashboard(tmp_path, monkeypatch):
    dashboard_path = tmp_path / "missing_dashboard.json"
    log_path = tmp_path / "batch_health_log.jsonl"

    monkeypatch.setattr(module, "DEFAULT_DASHBOARD_PATH", dashboard_path)
    monkeypatch.setattr(module, "DEFAULT_LOG_PATH", log_path)

    record = module.append_batch_health_log(tests_status="passed", batch_status="passed")

    assert log_path.exists()
    assert record["dashboard_exists"] is False
    assert record["summary_total_count"] == 0
    assert "does not exist" in record["notes"].lower()
