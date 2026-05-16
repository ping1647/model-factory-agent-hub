"""Deterministic PQA Agent v0.1 for dashboard and decision guardrail checks."""

from __future__ import annotations

from typing import Any


BUY_LIKE_DECISIONS = {"Buy", "Starter"}
BLOCKED_DECISIONS = {"Wait", "Risk-Blocked", "Avoid"}


def _add_check(checks: list[dict[str, Any]], failures: list[str], warnings: list[str], *, check_name: str, passed: bool, severity: str, message: str) -> None:
    checks.append({
        "check_name": check_name,
        "passed": passed,
        "severity": severity,
        "message": message,
    })
    if not passed:
        if severity == "Fail":
            failures.append(check_name)
        elif severity == "Warning":
            warnings.append(check_name)


def run_pqa_checks(
    audit: dict,
    data_audit: dict | None = None,
    dashboard_card: dict | None = None,
) -> dict:
    """Validate audit/data/dashboard consistency without external lookups."""
    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    warnings: list[str] = []

    decision = audit.get("decision")
    risk_score = int(audit.get("risk_score", 0))
    position_class = str(audit.get("position_class", ""))
    evidence_quality = audit.get("evidence_quality")
    missing_data = audit.get("missing_data", []) or []

    if decision in BUY_LIKE_DECISIONS and data_audit and data_audit.get("current_price") is None:
        _add_check(checks, failures, warnings, check_name="missing_current_price_blocks_action", passed=False, severity="Fail", message="Buy/Starter requires a current price.")

    if decision in BUY_LIKE_DECISIONS and data_audit and bool(data_audit.get("stale_price")):
        _add_check(checks, failures, warnings, check_name="stale_price_blocks_action", passed=False, severity="Fail", message="Buy/Starter cannot proceed with stale price.")

    if decision in BUY_LIKE_DECISIONS and data_audit and data_audit.get("benchmark_status") == "Missing":
        _add_check(checks, failures, warnings, check_name="missing_benchmark_blocks_action", passed=False, severity="Fail", message="Buy/Starter requires benchmark context.")

    if decision == "Buy" and data_audit and data_audit.get("valuation_status") == "Unreliable - Guidance Withdrawn":
        _add_check(checks, failures, warnings, check_name="guidance_withdrawn_blocks_buy", passed=False, severity="Fail", message="Buy is blocked when guidance is withdrawn.")

    if risk_score >= 8 and "Core" in position_class:
        _add_check(checks, failures, warnings, check_name="high_risk_cannot_be_core", passed=False, severity="Fail", message="Risk score >=8 cannot be Core position class.")

    if evidence_quality == "Missing Data" and decision == "Buy":
        _add_check(checks, failures, warnings, check_name="missing_data_cannot_be_buy", passed=False, severity="Fail", message="Missing Data evidence quality cannot be Buy.")

    if dashboard_card and dashboard_card.get("status") == "Top Candidate" and decision in BLOCKED_DECISIONS:
        _add_check(checks, failures, warnings, check_name="blocked_name_cannot_be_top_candidate", passed=False, severity="Fail", message="Blocked decisions cannot be Top Candidate.")

    if dashboard_card and dashboard_card.get("freshness") == "Fresh" and data_audit and bool(data_audit.get("stale_price")):
        _add_check(checks, failures, warnings, check_name="stale_price_cannot_be_fresh", passed=False, severity="Fail", message="Dashboard freshness cannot be Fresh when price is stale.")

    if decision == "Starter" and len(missing_data) >= 5:
        _add_check(checks, failures, warnings, check_name="starter_has_many_missing_data_items", passed=False, severity="Warning", message="Starter has many missing data items (>=5).")

    passed = len(failures) == 0

    if failures:
        severity = "Fail"
        next_action = "Block publication/action; resolve failures"
    elif warnings:
        severity = "Warning"
        next_action = "Review warnings before publishing"
    else:
        severity = "Pass"
        next_action = "Ready for publication"

    return {
        "ticker": audit.get("ticker", ""),
        "passed": passed,
        "checks": checks,
        "failures": failures,
        "warnings": warnings,
        "severity": severity,
        "next_action": next_action,
    }
