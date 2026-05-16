from __future__ import annotations

import json
from pathlib import Path

from agents.batch_runner import (
    load_watchlist,
    run_and_persist_batch,
    run_batch_from_watchlist,
)


def load_example(name: str) -> dict:
    path = Path(__file__).resolve().parents[1] / "data" / "examples" / name
    return json.loads(path.read_text(encoding="utf-8"))


def base_run_context() -> dict:
    return {
        "model_registry_master": {"freshness": "fresh"},
        "model_checkpoint_latest": {"freshness": "fresh"},
        "changelog_master": {"freshness": "fresh"},
        "model_factor_matrix": {"freshness": "fresh"},
        "contradiction_log": {"freshness": "fresh"},
        "target_models": ["M13"],
    }


def base_market_inputs() -> dict:
    return {
        "current_price": 48.0,
        "price_as_of": "2026-05-16",
        "benchmark_etf": ["PHO", "PIO"],
        "buy_zone_low": 40.0,
        "buy_zone_high": 50.0,
    }


def test_load_watchlist_filters_active_and_normalizes(tmp_path):
    watchlist_path = tmp_path / "watchlist.json"
    watchlist_path.write_text(
        json.dumps(
            [
                {"ticker": " ttek ", "model_id": " m13 ", "status": "active"},
                {"ticker": "erii", "model_id": "m13", "status": "paused"},
            ]
        ),
        encoding="utf-8",
    )

    loaded = load_watchlist(str(watchlist_path))

    assert len(loaded) == 1
    assert loaded[0]["ticker"] == "TTEK"
    assert loaded[0]["model_id"] == "M13"


def test_run_batch_from_watchlist_ttek_erii_returns_two_results():
    watchlist = [
        {"ticker": "TTEK", "model_id": "M13", "benchmark_etf": ["PHO", "PIO"], "status": "active"},
        {"ticker": "ERII", "model_id": "M13", "benchmark_etf": ["PHO", "PIO"], "status": "active"},
    ]
    market_inputs_by_ticker = {
        "TTEK": base_market_inputs(),
        "ERII": {**base_market_inputs(), "guidance_withdrawn": True},
    }
    base_audits_by_ticker = {
        "TTEK": load_example("TTEK.audit.json"),
        "ERII": load_example("ERII.audit.json"),
    }

    results = run_batch_from_watchlist(
        watchlist=watchlist,
        run_context=base_run_context(),
        model_factor_matrix={"M13": {}},
        market_inputs_by_ticker=market_inputs_by_ticker,
        base_audits_by_ticker=base_audits_by_ticker,
    )

    assert len(results) == 2
    assert {item["ticker"] for item in results} == {"TTEK", "ERII"}


def test_missing_market_input_generates_fail_pipeline():
    watchlist = [
        {"ticker": "TTEK", "model_id": "M13", "benchmark_etf": ["PHO", "PIO"], "status": "active"}
    ]

    results = run_batch_from_watchlist(
        watchlist=watchlist,
        run_context=base_run_context(),
        model_factor_matrix={"M13": {}},
        market_inputs_by_ticker={},
        base_audits_by_ticker={"TTEK": load_example("TTEK.audit.json")},
    )

    assert results[0]["pipeline_status"] == "Fail"
    blockers = set(results[0]["blockers"])
    assert "missing_current_price" in blockers or "missing_price_timestamp" in blockers


def test_run_and_persist_batch_writes_run_records_and_dashboard(tmp_path):
    watchlist = [
        {"ticker": "TTEK", "model_id": "M13", "benchmark_etf": ["PHO", "PIO"], "status": "active"},
        {"ticker": "ERII", "model_id": "M13", "benchmark_etf": ["PHO", "PIO"], "status": "active"},
    ]

    result = run_and_persist_batch(
        watchlist=watchlist,
        run_id="RUNBATCH001",
        run_date="2026-05-16",
        run_context=base_run_context(),
        model_factor_matrix={"M13": {}},
        market_inputs_by_ticker={"TTEK": base_market_inputs(), "ERII": base_market_inputs()},
        base_audits_by_ticker={"TTEK": load_example("TTEK.audit.json"), "ERII": load_example("ERII.audit.json")},
        run_output_dir=str(tmp_path / "runs"),
        dashboard_output_path=str(tmp_path / "dashboard" / "latest.json"),
    )

    assert len(result["run_record_paths"]) == 2
    for path in result["run_record_paths"]:
        assert Path(path).exists()

    dashboard_path = Path(result["dashboard_output_path"])
    assert dashboard_path.exists()
    persisted = json.loads(dashboard_path.read_text(encoding="utf-8"))
    assert persisted["summary"]["total_count"] == 2
