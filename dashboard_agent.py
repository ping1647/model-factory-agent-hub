"""Map stock audits to dashboard cards."""

from __future__ import annotations
from typing import Dict, Any

def risk_color(score: int) -> str:
    if score <= 3:
        return "Green"
    if score <= 5:
        return "Yellow"
    if score <= 7:
        return "Orange"
    return "Red"

def to_dashboard_card(audit: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ticker": audit["ticker"],
        "company": audit.get("company", ""),
        "model_id": audit.get("model_id", ""),
        "decision": audit["decision"],
        "risk_score": audit["risk_score"],
        "risk_color": risk_color(int(audit["risk_score"])),
        "status": "Risk-Blocked" if audit.get("blocked_by") and audit["decision"] in ["Wait", "Risk-Blocked"] else audit["decision"],
        "position_class": audit.get("position_class", ""),
        "benchmark_etf": audit.get("benchmark_etf", []),
        "blocked_by": audit.get("blocked_by", []),
        "missing_data": audit.get("missing_data", []),
        "next_action": audit.get("next_action", ""),
        "freshness": "Needs price/data freshness check"
    }
