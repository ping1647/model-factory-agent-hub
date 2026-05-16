from pathlib import Path


def test_scheduled_batch_workflow_contains_expected_configuration() -> None:
    workflow_text = Path(".github/workflows/scheduled-batch-run.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch" in workflow_text
    assert "schedule" in workflow_text
    assert "30 0 * * *" in workflow_text
    assert "pytest tests -q" in workflow_text
    assert "python scripts/run_manual_batch.py" in workflow_text
    assert "PYTHONPATH: ." in workflow_text
    assert "scripts/append_batch_health_log.py" in workflow_text
    assert "data/logs/batch_health_log.jsonl" in workflow_text
    assert (
        "git add data/runs data/dashboard/latest_dashboard_data.json app/dashboard/public/dashboard_data.json data/logs/batch_health_log.jsonl"
        in workflow_text
    )
