"""Utilities for exporting dashboard snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agents.dashboard_data_builder import build_dashboard_data



def export_dashboard_data(dashboard_data: dict[str, Any], output_path: str) -> str:
    """Write dashboard data as pretty UTF-8 JSON and return output path."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8") as handle:
        json.dump(dashboard_data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")

    return output_path



def export_latest_dashboard_from_pipeline_results(
    pipeline_results: list[dict[str, Any]], output_path: str
) -> dict[str, Any]:
    """Build and export the latest dashboard JSON from pipeline results."""
    dashboard_data = build_dashboard_data(pipeline_results)
    export_dashboard_data(dashboard_data, output_path)
    return dashboard_data
