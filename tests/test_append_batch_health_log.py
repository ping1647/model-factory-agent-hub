import json

from scripts import append_batch_health_log as module


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


def test_append_batch_health_log_reads_summary_and_writes_jsonl(tmp_path, monkeypatch):
    dashboard_path = tmp_path / "latest_dashboard_data.json"
    log_path = tmp_path / "batch_health_log.jsonl"

    dashboard_payload = {
        "summary": {
            "total_count": 10,
            "pass_count": 7,
            "fail_count": 2,
            "needs_audit_count": 1,
        }
    }
    dashboard_path.write_text(json.dumps(dashboard_payload), encoding="utf-8")

    monkeypatch.setattr(module, "DEFAULT_DASHBOARD_PATH", dashboard_path)
    monkeypatch.setattr(module, "DEFAULT_LOG_PATH", log_path)

    module.append_batch_health_log(tests_status="success", batch_status="success")

    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    row = json.loads(lines[0])
    assert REQUIRED_FIELDS.issubset(row.keys())
    assert row["summary_total_count"] == 10
    assert row["summary_pass_count"] == 7
    assert row["summary_fail_count"] == 2
    assert row["summary_needs_audit_count"] == 1


def test_append_batch_health_log_handles_missing_dashboard(tmp_path, monkeypatch):
    dashboard_path = tmp_path / "missing_dashboard.json"
    log_path = tmp_path / "batch_health_log.jsonl"

    monkeypatch.setattr(module, "DEFAULT_DASHBOARD_PATH", dashboard_path)
    monkeypatch.setattr(module, "DEFAULT_LOG_PATH", log_path)

    record = module.append_batch_health_log(tests_status="failure", batch_status="skipped")

    assert log_path.exists()
    assert record["dashboard_exists"] is False
    assert record["summary_total_count"] == 0
    assert "does not exist" in record["notes"].lower()


def test_append_batch_health_log_handles_malformed_dashboard(tmp_path, monkeypatch):
    dashboard_path = tmp_path / "bad_dashboard.json"
    log_path = tmp_path / "batch_health_log.jsonl"

    dashboard_path.write_text("{not valid json", encoding="utf-8")

    monkeypatch.setattr(module, "DEFAULT_DASHBOARD_PATH", dashboard_path)
    monkeypatch.setattr(module, "DEFAULT_LOG_PATH", log_path)

    record = module.append_batch_health_log(tests_status="success", batch_status="failure")

    assert log_path.exists()
    assert record["dashboard_exists"] is True
    assert record["summary_total_count"] == 0
    assert "malformed" in record["notes"].lower()
