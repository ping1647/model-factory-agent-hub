"""Deterministic Pipeline Orchestrator v0.1 for local stock audit workflow."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from agents.dashboard_agent import to_dashboard_card
from agents.data_auditor import build_data_audit
from agents.memory_librarian import run_memory_check
from agents.pqa_agent import run_pqa_checks
from agents.research_scout import build_research_summary_skeleton
from agents.risk_agent import apply_risk_rules
from agents.source_collector import build_source_requirements


PASS = "Pass"
WARNING = "Warning"
FAIL = "Fail"
NEEDS_AUDIT = "Needs Audit"


def run_stock_audit_pipeline(
    ticker: str,
    model_id: str,
    run_context: dict,
    model_factor_matrix: dict,
    market_inputs: dict,
    base_audit: dict | None = None,
) -> dict:
    """Run deterministic local pipeline without external data or LLM APIs."""
    memory_check = run_memory_check(run_context, model_factor_matrix)

    source_requirements = build_source_requirements(ticker, model_id)
    research_summary = build_research_summary_skeleton(
        ticker,
        model_id,
        source_requirements["source_requirements"],
    )

    data_audit = build_data_audit(
        ticker=ticker,
        model_id=model_id,
        current_price=market_inputs.get("current_price"),
        price_as_of=market_inputs.get("price_as_of"),
        benchmark_etf=market_inputs.get("benchmark_etf", []),
        buy_zone_low=market_inputs.get("buy_zone_low"),
        buy_zone_high=market_inputs.get("buy_zone_high"),
        eps_guidance_midpoint=market_inputs.get("eps_guidance_midpoint"),
        guidance_withdrawn=bool(market_inputs.get("guidance_withdrawn", False)),
    )

    risk_adjusted_audit: dict[str, Any] | None = None
    dashboard_card: dict[str, Any] | None = None
    pqa_report: dict[str, Any] | None = None

    if base_audit is not None:
        risk_adjusted_audit = apply_risk_rules(deepcopy(base_audit))
        dashboard_card = to_dashboard_card(risk_adjusted_audit)
        pqa_report = run_pqa_checks(risk_adjusted_audit, data_audit, dashboard_card)

    blockers: list[str] = []
    blockers.extend(memory_check.get("failures", []))
    blockers.extend(data_audit.get("decision_blockers", []))
    if pqa_report:
        blockers.extend(pqa_report.get("failures", []))
    blockers = sorted(set(blockers))

    if memory_check.get("severity") == FAIL:
        pipeline_status = FAIL
    elif data_audit.get("data_quality") == "Blocked":
        pipeline_status = FAIL
    elif base_audit is None:
        pipeline_status = NEEDS_AUDIT
    elif pqa_report and pqa_report.get("severity") == FAIL:
        pipeline_status = FAIL
    elif (pqa_report and pqa_report.get("severity") == WARNING) or memory_check.get("severity") == WARNING:
        pipeline_status = WARNING
    else:
        pipeline_status = PASS

    if pipeline_status == FAIL:
        next_action = "Resolve blockers before proceeding with any decision output."
    elif pipeline_status == NEEDS_AUDIT:
        next_action = "Provide base_audit input, then run risk/dashboard/PQA stages."
    elif pipeline_status == WARNING:
        next_action = "Review warning items and confirm human approval before publication."
    else:
        next_action = "Pipeline passed; proceed to human review/approval for any action."

    return {
        "ticker": ticker.strip().upper(),
        "model_id": model_id.strip().upper(),
        "memory_check": memory_check,
        "source_requirements": source_requirements,
        "research_summary": research_summary,
        "data_audit": data_audit,
        "risk_adjusted_audit": risk_adjusted_audit,
        "dashboard_card": dashboard_card,
        "pqa_report": pqa_report,
        "pipeline_status": pipeline_status,
        "blockers": blockers,
        "next_action": next_action,
    }
