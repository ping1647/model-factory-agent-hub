from __future__ import annotations

import json
from pathlib import Path

from agents.pipeline_orchestrator import run_stock_audit_pipeline


def load_example(name: str) -> dict:
    path = Path(__file__).resolve().parents[1] / "data" / "examples" / name
    return json.loads(path.read_text(encoding="utf-8"))


def base_run_context() -> dict:
    return {
        "model_registry_master": {"freshness": "fresh"},
        "model_checkpoint_latest": {"freshness": "fresh"},
        "changelog_master": {"freshness": "fresh"},
        "model_factor_matrix": {"freshness": "fresh"},
        "contradiction_log": {"freshness": "fresh"},
        "target_models": ["M13"],
    }


def base_market_inputs() -> dict:
    return {
        "current_price": 48.0,
        "price_as_of": "2026-05-16",
        "benchmark_etf": ["PHO", "PIO"],
        "buy_zone_low": 40.0,
        "buy_zone_high": 50.0,
        "eps_guidance_midpoint": 2.8,
        "guidance_withdrawn": False,
    }


def test_ttek_pipeline_with_base_audit_not_fail():
    out = run_stock_audit_pipeline(
        ticker="TTEK",
        model_id="M13",
        run_context=base_run_context(),
        model_factor_matrix={"M13": {}},
        market_inputs=base_market_inputs(),
        base_audit=load_example("TTEK.audit.json"),
    )

    assert out["pipeline_status"] in {"Pass", "Warning"}
    assert out["pipeline_status"] != "Fail"


def test_erii_guidance_withdrawn_not_top_candidate_buy():
    erii = load_example("ERII.audit.json")
    out = run_stock_audit_pipeline(
        ticker="ERII",
        model_id="M13",
        run_context=base_run_context(),
        model_factor_matrix={"M13": {}},
        market_inputs={**base_market_inputs(), "guidance_withdrawn": True},
        base_audit=erii,
    )

    assert out["risk_adjusted_audit"]["decision"] in {"Wait", "Risk-Blocked", "Avoid", "Starter", "Buy"}
    assert out["dashboard_card"]["status"] != "Top Candidate"
    assert out["risk_adjusted_audit"]["decision"] != "Buy"


def test_missing_current_price_fails():
    out = run_stock_audit_pipeline(
        ticker="TTEK",
        model_id="M13",
        run_context=base_run_context(),
        model_factor_matrix={"M13": {}},
        market_inputs={**base_market_inputs(), "current_price": None},
        base_audit=load_example("TTEK.audit.json"),
    )

    assert out["pipeline_status"] == "Fail"


def test_missing_memory_context_fails():
    run_context = base_run_context()
    run_context.pop("model_registry_master")

    out = run_stock_audit_pipeline(
        ticker="TTEK",
        model_id="M13",
        run_context=run_context,
        model_factor_matrix={"M13": {}},
        market_inputs=base_market_inputs(),
        base_audit=load_example("TTEK.audit.json"),
    )

    assert out["pipeline_status"] == "Fail"


def test_no_base_audit_needs_audit():
    out = run_stock_audit_pipeline(
        ticker="TTEK",
        model_id="M13",
        run_context=base_run_context(),
        model_factor_matrix={"M13": {}},
        market_inputs=base_market_inputs(),
        base_audit=None,
    )

    assert out["pipeline_status"] == "Needs Audit"
    assert out["risk_adjusted_audit"] is None
    assert out["dashboard_card"] is None
    assert out["pqa_report"] is None
