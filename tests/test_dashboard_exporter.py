import json

from agents.dashboard_exporter import (
    export_dashboard_data,
    export_latest_dashboard_from_pipeline_results,
)


def _result() -> dict:
    return {
        "ticker": "TTEK",
        "model_id": "M13",
        "pipeline_status": "Pass",
        "data_audit": {"buy_zone_status": "In Buy Zone", "valuation_status": "Fair"},
        "risk_adjusted_audit": {"decision": "Buy", "risk_score": 3, "position_class": "Starter"},
        "dashboard_card": {"status": "Buy"},
        "blockers": [],
        "next_action": "review",
    }


def test_export_dashboard_data_creates_json_file(tmp_path):
    dashboard_data = {"summary": {"total_count": 1}}
    output_path = tmp_path / "dashboard" / "latest.json"

    result_path = export_dashboard_data(dashboard_data, str(output_path))

    assert result_path == str(output_path)
    assert output_path.exists()


def test_export_latest_dashboard_from_pipeline_results_writes_dashboard(tmp_path):
    output_path = tmp_path / "dashboard" / "latest.json"

    data = export_latest_dashboard_from_pipeline_results([_result()], str(output_path))

    assert data["summary"]["total_count"] == 1
    with output_path.open(encoding="utf-8") as handle:
        persisted = json.load(handle)
    assert persisted["summary"]["pass_count"] == 1
