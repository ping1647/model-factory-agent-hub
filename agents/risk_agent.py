"""Deterministic first-pass Risk Agent guardrails."""

from __future__ import annotations
from typing import Dict, Any, List

def apply_risk_rules(audit: Dict[str, Any]) -> Dict[str, Any]:
    decision = audit.get("decision")
    risk_score = int(audit.get("risk_score", 10))
    blocked_by: List[str] = list(audit.get("blocked_by", []))
    missing_data: List[str] = list(audit.get("missing_data", []))
    text = " ".join(audit.get("verified_facts", []) + audit.get("bear_case", []) + blocked_by).lower()

    if "guidance withdrawn" in text:
        decision = "Wait"
        blocked_by.append("guidance withdrawn")

    if risk_score >= 8 and "core" in audit.get("position_class", "").lower():
        audit["position_class"] = "Speculative / Avoid"

    if len(missing_data) >= 5 and decision == "Buy":
        decision = "Starter"

    if not audit.get("benchmark_etf"):
        decision = "Wait"
        blocked_by.append("missing benchmark")

    audit["decision"] = decision
    audit["blocked_by"] = sorted(set(blocked_by))
    audit["human_approval_required"] = True
    return audit
