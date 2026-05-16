import json

from agents.run_store import create_run_record, write_run_record


def test_create_run_record_preserves_core_fields():
    pipeline_result = {
        "pipeline_status": "Pass",
        "blockers": ["none"],
        "next_action": "queue",
        "extra": {"alpha": 1.2},
    }

    record = create_run_record("RUN001", "2026-05-16", "TTEK", "M13", pipeline_result)

    assert record["ticker"] == "TTEK"
    assert record["model_id"] == "M13"
    assert record["pipeline_status"] == "Pass"
    assert record["blockers"] == ["none"]


def test_write_run_record_creates_file_and_preserves_nested_payload(tmp_path):
    pipeline_result = {
        "pipeline_status": "Warning",
        "blockers": ["missing source"],
        "next_action": "collect",
        "nested": {"facts": ["a", "b"]},
    }
    record = create_run_record("RUN777", "2026-05-16", "SOFI", "M5", pipeline_result)

    output_path = write_run_record(record, str(tmp_path))

    with open(output_path, encoding="utf-8") as handle:
        loaded = json.load(handle)

    assert loaded["run_id"] == "RUN777"
    assert loaded["pipeline_result"]["nested"]["facts"] == ["a", "b"]
