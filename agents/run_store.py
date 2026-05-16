"""Persistent run-record utilities for pipeline outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any



def create_run_record(
    run_id: str,
    run_date: str,
    ticker: str,
    model_id: str,
    pipeline_result: dict[str, Any],
) -> dict[str, Any]:
    """Build a deterministic run-record payload from pipeline output."""
    return {
        "run_id": run_id,
        "run_date": run_date,
        "ticker": ticker,
        "model_id": model_id,
        "pipeline_status": pipeline_result.get("pipeline_status", ""),
        "blockers": pipeline_result.get("blockers", []),
        "next_action": pipeline_result.get("next_action", ""),
        "pipeline_result": pipeline_result,
    }



def write_run_record(record: dict[str, Any], output_dir: str) -> str:
    """Write a run record to a date-partitioned JSON file and return its path."""
    run_date = record["run_date"]
    ticker = record["ticker"]
    model_id = record["model_id"]
    run_id = record["run_id"]

    destination = Path(output_dir) / run_date / f"{ticker}.{model_id}.{run_id}.pipeline.json"
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    return str(destination)
