"""Aggregate structured QA evidence into fail-closed report readiness."""

from __future__ import annotations

from typing import Any

from agents.quality_score_validator import validate_quality_scores

ALLOWED_STATUSES = {
    "ศึกษาต่อ", "รอราคา", "รอหลักฐาน",
    "ผ่านเงื่อนไขพิจารณาลงทุน", "งดพิจารณาซื้อขณะนี้",
}


def _findings_gate(findings: Any) -> tuple[str, list[str]]:
    if not isinstance(findings, list) or not findings:
        return "UNKNOWN", ["missing_structured_findings"]
    blockers = []
    for item in findings:
        if not isinstance(item, dict):
            blockers.append("invalid_finding")
        elif item.get("result") != "PASS":
            blockers.append(str(item.get("code", "invalid_finding")))
    return ("PASS", []) if not blockers else ("FAIL", blockers)


def aggregate_report_readiness(dataset: dict[str, Any]) -> dict[str, Any]:
    """Calculate stock and report gates; unknown required gates fail closed."""
    stocks = dataset.get("stocks")
    processing_errors = []
    if dataset.get("dataset_label") != "SYNTHETIC_DEMO":
        processing_errors.append("dataset_not_labelled_synthetic_demo")
    if not isinstance(stocks, list) or not stocks:
        processing_errors.append("missing_or_empty_stocks")
        stocks = []

    shared_checks = dataset.get("shared_checks")
    shared_status, shared_blockers = _findings_gate(shared_checks)
    quality_rows = [stock.get("quality", {}) if isinstance(stock, dict) else {} for stock in stocks]
    quality_report = validate_quality_scores(quality_rows)

    stock_results = []
    for index, stock in enumerate(stocks):
        stock = stock if isinstance(stock, dict) else {}
        ticker = str(stock.get("ticker", "")).strip().upper()
        quality = quality_report["rows"][index]
        evidence_status, evidence_blockers = _findings_gate(stock.get("evidence_checks"))
        thesis_status, thesis_blockers = _findings_gate(stock.get("thesis_checks"))
        valuation_status, valuation_blockers = _findings_gate(stock.get("valuation_checks"))
        data_blockers = evidence_blockers + ([] if quality["status"] == "PASS" else ["quality_score_validation_failed"])
        data_status = "PASS" if not data_blockers else "FAIL"
        analytical_blockers = thesis_blockers + valuation_blockers
        analytical_status = "PASS" if not analytical_blockers else "FAIL"
        status = stock.get("status") if stock.get("status") in ALLOWED_STATUSES else "รอหลักฐาน"
        blockers = sorted(set(data_blockers + analytical_blockers + shared_blockers + processing_errors))
        stock_results.append({
            "ticker": ticker,
            "company": stock.get("company", ""),
            "status": status,
            "status_reason": stock.get("status_reason", "N/A"),
            "transition_condition": stock.get("transition_condition", "N/A"),
            "quality": quality,
            "opportunity": stock.get("opportunity", {"value": "N/A", "reason": "methodology_not_defined"}),
            "history_5y": stock.get("history_5y", {"value": "N/A", "reason": "missing_history"}),
            "gates": {
                "data_qa": data_status,
                "thesis_valuation_qa": analytical_status,
            },
            "blockers": blockers,
            "actionable_buy": False,
            "analytical_gates_passed": data_status == analytical_status == "PASS" and not shared_blockers,
        })

    processing_status = "PASS" if not processing_errors else "FAIL"
    data_status = "PASS" if stock_results and all(s["gates"]["data_qa"] == "PASS" for s in stock_results) else "FAIL"
    thesis_status = "PASS" if stock_results and all(s["gates"]["thesis_valuation_qa"] == "PASS" for s in stock_results) else "FAIL"
    return {
        "dataset_label": dataset.get("dataset_label"),
        "disclaimer": "ข้อมูลจำลองสำหรับทดสอบระบบ ไม่ใช่คำแนะนำลงทุน",
        "run_id": dataset.get("run_id"),
        "scope": dataset.get("scope", "N/A"),
        "gates": {
            "processing": {"status": processing_status, "blockers": processing_errors},
            "data_qa": {"status": data_status},
            "thesis_valuation_qa": {"status": thesis_status},
            "delivery_qa": {"status": "UNKNOWN", "blockers": ["artifacts_not_yet_verified"]},
        },
        "shared_critical_status": shared_status,
        "shared_critical_blockers": shared_blockers,
        "quality_validation": quality_report,
        "stocks": stock_results,
        "processing_completed": processing_status == "PASS",
        "report_validation_passed": processing_status == data_status == thesis_status == shared_status == "PASS",
        "production_ready": False,
        "actionable_buys_allowed": False,
        "stub_blockers": ["opportunity_methodology_not_approved", "analysis_reliability_score_not_approved"],
    }


def apply_delivery_qa(report: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    """Attach structured delivery checks without promoting production readiness."""
    status, blockers = _findings_gate(checks)
    report["gates"]["delivery_qa"] = {"status": status, "blockers": blockers, "checks": checks}
    report["delivery_verified"] = status == "PASS"
    # Stub methodologies deliberately keep this synthetic report non-production.
    report["production_ready"] = False
    report["actionable_buys_allowed"] = False
    return report
