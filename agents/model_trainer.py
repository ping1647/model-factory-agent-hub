"""Deterministic Model Trainer scaffold v0.1."""

from __future__ import annotations

from typing import Any, Dict, List


def create_training_event(
    ticker: str,
    model_id: str,
    decision_date: str,
    decision: str,
    benchmark_etf: List[str],
    thesis_summary: str,
    risk_score: int,
    position_class: str,
    evidence_quality: str,
    missing_data: List[str],
    expected_review_windows: List[str] | None = None,
) -> Dict[str, Any]:
    return {
        "ticker": ticker,
        "model_id": model_id,
        "decision_date": decision_date,
        "decision": decision,
        "benchmark_etf": benchmark_etf,
        "thesis_summary": thesis_summary,
        "risk_score": risk_score,
        "position_class": position_class,
        "evidence_quality": evidence_quality,
        "missing_data": missing_data,
        "expected_review_windows": expected_review_windows or ["1M", "3M", "6M", "12M"],
        "outcome_status": "Pending",
        "lessons": [],
        "rule_update_needed": False,
        "human_review_required": True,
    }


def evaluate_training_outcome(
    training_event: Dict[str, Any],
    stock_return_pct: float,
    benchmark_return_pct: float,
    max_drawdown_pct: float | None = None,
    kill_switch_triggered: bool = False,
) -> Dict[str, Any]:
    alpha_pct = stock_return_pct - benchmark_return_pct

    if kill_switch_triggered:
        outcome_status = "Loss"
        rule_update_needed = True
    elif alpha_pct >= 5 and (max_drawdown_pct is None or max_drawdown_pct >= -25):
        outcome_status = "Win"
        rule_update_needed = False
    elif alpha_pct <= -5 or (max_drawdown_pct is not None and max_drawdown_pct < -35):
        outcome_status = "Loss"
        rule_update_needed = False
    else:
        outcome_status = "Mixed"
        rule_update_needed = False

    lessons: List[str] = []
    if outcome_status == "Loss":
        lessons.append("Review thesis, risk gate, valuation, and benchmark fallback.")
    elif outcome_status == "Win":
        lessons.append(
            "Pattern validated; consider whether rule weight should increase after more cases."
        )
    else:
        lessons.append("Outcome inconclusive; keep tracking and avoid overfitting.")

    return {
        "ticker": training_event.get("ticker"),
        "model_id": training_event.get("model_id"),
        "decision": training_event.get("decision"),
        "stock_return_pct": stock_return_pct,
        "benchmark_return_pct": benchmark_return_pct,
        "alpha_pct": alpha_pct,
        "max_drawdown_pct": max_drawdown_pct,
        "kill_switch_triggered": kill_switch_triggered,
        "outcome_status": outcome_status,
        "lessons": lessons,
        "rule_update_needed": rule_update_needed,
        "human_review_required": True,
    }
