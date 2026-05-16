"""Deterministic batch runner v0.1 for master watchlist execution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agents.dashboard_exporter import export_latest_dashboard_from_pipeline_results
from agents.pipeline_orchestrator import run_stock_audit_pipeline
from agents.run_store import create_run_record, write_run_record


def load_watchlist(path: str) -> list[dict[str, Any]]:
    """Load watchlist JSON and return normalized active items only."""
    items = json.loads(Path(path).read_text(encoding="utf-8"))

    active_items: list[dict[str, Any]] = []
    for raw_item in items:
        status = str(raw_item.get("status", "")).strip().lower()
        if status != "active":
            continue

        item = dict(raw_item)
        item["ticker"] = str(item.get("ticker", "")).strip().upper()
        item["model_id"] = str(item.get("model_id", "")).strip().upper()
        active_items.append(item)

    return active_items


def run_batch_from_watchlist(
    watchlist: list[dict],
    run_context: dict,
    model_factor_matrix: dict,
    market_inputs_by_ticker: dict,
    base_audits_by_ticker: dict | None = None,
) -> list[dict]:
    """Run stock-audit pipeline for each active watchlist item deterministically."""
    pipeline_results: list[dict] = []

    for item in watchlist:
        ticker = str(item.get("ticker", "")).strip().upper()
        model_id = str(item.get("model_id", "")).strip().upper()

        market_inputs = dict(market_inputs_by_ticker.get(ticker, {}))
        if not market_inputs:
            market_inputs = {
                "current_price": None,
                "price_as_of": None,
                "benchmark_etf": item.get("benchmark_etf", []),
                "buy_zone_low": None,
                "buy_zone_high": None,
            }

        base_audit = None
        if base_audits_by_ticker is not None:
            base_audit = base_audits_by_ticker.get(ticker)

        result = run_stock_audit_pipeline(
            ticker=ticker,
            model_id=model_id,
            run_context=run_context,
            model_factor_matrix=model_factor_matrix,
            market_inputs=market_inputs,
            base_audit=base_audit,
        )
        pipeline_results.append(result)

    return pipeline_results


def run_and_persist_batch(
    watchlist: list[dict],
    run_id: str,
    run_date: str,
    run_context: dict,
    model_factor_matrix: dict,
    market_inputs_by_ticker: dict,
    base_audits_by_ticker: dict | None,
    run_output_dir: str,
    dashboard_output_path: str,
) -> dict:
    """Run watchlist batch, persist run records, and export latest dashboard."""
    pipeline_results = run_batch_from_watchlist(
        watchlist=watchlist,
        run_context=run_context,
        model_factor_matrix=model_factor_matrix,
        market_inputs_by_ticker=market_inputs_by_ticker,
        base_audits_by_ticker=base_audits_by_ticker,
    )

    run_record_paths: list[str] = []
    for result in pipeline_results:
        record = create_run_record(
            run_id=run_id,
            run_date=run_date,
            ticker=result.get("ticker", ""),
            model_id=result.get("model_id", ""),
            pipeline_result=result,
        )
        run_record_paths.append(write_run_record(record, run_output_dir))

    dashboard_data = export_latest_dashboard_from_pipeline_results(
        pipeline_results=pipeline_results,
        output_path=dashboard_output_path,
    )

    return {
        "run_id": run_id,
        "run_date": run_date,
        "pipeline_results": pipeline_results,
        "run_record_paths": run_record_paths,
        "dashboard_output_path": dashboard_output_path,
        "dashboard_data": dashboard_data,
    }
