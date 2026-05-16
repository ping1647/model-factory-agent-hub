"""Deterministic Research Scout scaffold for stock audit draft skeletons."""

from __future__ import annotations

from typing import Any, Dict, List


def build_research_summary_skeleton(
    ticker: str,
    model_id: str,
    source_requirements: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Build a deterministic research summary skeleton from source requirements."""
    normalized_ticker = ticker.strip().upper()
    normalized_model = model_id.strip().upper()
    checklist = [dict(item) for item in source_requirements]

    missing_data: List[str] = []
    for item in checklist:
        if item.get("required") is True:
            is_collected = bool(item.get("collected", False))
            if not is_collected:
                source_type = item.get("source_type")
                if source_type:
                    missing_data.append(str(source_type))

    return {
        "ticker": normalized_ticker,
        "model_id": normalized_model,
        "evidence_quality": "Missing Data",
        "verified_facts": [],
        "model_estimates": [],
        "weak_signals": [],
        "missing_data": missing_data,
        "source_checklist": checklist,
        "growth_drivers": [],
        "profitability_quality": "Missing Data",
        "balance_sheet": "Missing Data",
        "moat": "Missing Data",
        "valuation": "Missing Data",
        "bull_case": [],
        "bear_case": [],
        "kill_switches": [],
        "preliminary_decision": "Wait",
        "next_action": "Collect and verify required sources before audit decision.",
    }
