"""Build dashboard-ready data structures from pipeline results."""

from __future__ import annotations

from typing import Any


FAIL = "Fail"
WARNING = "Warning"
NEEDS_AUDIT = "Needs Audit"
PASS = "Pass"
RISK_BLOCKED = "Risk-Blocked"
WAIT = "Wait"


def _item_from_result(result: dict[str, Any]) -> dict[str, Any]:
    data_audit = result.get("data_audit") or {}
    risk_adjusted = result.get("risk_adjusted_audit") or {}
    dashboard_card = result.get("dashboard_card") or {}

    return {
        "ticker": result.get("ticker", ""),
        "model_id": result.get("model_id", ""),
        "pipeline_status": result.get("pipeline_status", ""),
        "decision": risk_adjusted.get("decision", ""),
        "risk_score": risk_adjusted.get("risk_score"),
        "position_class": risk_adjusted.get("position_class", ""),
        "buy_zone_status": data_audit.get("buy_zone_status", ""),
        "valuation_status": data_audit.get("valuation_status", ""),
        "blockers": result.get("blockers", []),
        "next_action": result.get("next_action", ""),
        "_dashboard_status": dashboard_card.get("status", ""),
    }


def _is_risk_blocked(item: dict[str, Any]) -> bool:
    decision = item.get("decision")
    return item.get("_dashboard_status") == RISK_BLOCKED or decision in {WAIT, RISK_BLOCKED}


def build_dashboard_data(pipeline_results: list[dict]) -> dict:
    items = [_item_from_result(result) for result in pipeline_results]

    failed = [i for i in items if i["pipeline_status"] == FAIL]
    needs_audit = [i for i in items if i["pipeline_status"] == NEEDS_AUDIT]
    warnings = [i for i in items if i["pipeline_status"] == WARNING]

    risk_blocked: list[dict[str, Any]] = []
    for item in items:
        if item["pipeline_status"] == FAIL:
            continue
        if _is_risk_blocked(item):
            risk_blocked.append(item)

    buy_zone_board = [
        i
        for i in items
        if i["buy_zone_status"] == "In Buy Zone" and i["pipeline_status"] in {PASS, WARNING}
    ]

    risk_blocked_keys = {(i["ticker"], i["model_id"]) for i in risk_blocked}
    failed_keys = {(i["ticker"], i["model_id"]) for i in failed}

    top_candidates = [
        i
        for i in buy_zone_board
        if (i["ticker"], i["model_id"]) not in risk_blocked_keys
        and (i["ticker"], i["model_id"]) not in failed_keys
    ]

    needs_review = warnings + needs_audit + failed

    def _strip_internal(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{k: v for k, v in entry.items() if not k.startswith("_")} for entry in entries]

    return {
        "summary": {
            "total_count": len(items),
            "pass_count": sum(1 for i in items if i["pipeline_status"] == PASS),
            "warning_count": len(warnings),
            "fail_count": len(failed),
            "needs_audit_count": len(needs_audit),
            "risk_blocked_count": len(risk_blocked),
        },
        "command_center": {
            "top_candidates": _strip_internal(top_candidates),
            "blocked_names": _strip_internal(risk_blocked),
            "needs_review": _strip_internal(needs_review),
        },
        "buy_zone_board": _strip_internal(buy_zone_board),
        "risk_blocked": _strip_internal(risk_blocked),
        "needs_audit": _strip_internal(needs_audit),
        "failed": _strip_internal(failed),
        "warnings": _strip_internal(warnings),
        "latest_agent_runs_placeholder": [],
    }
