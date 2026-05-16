import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from agents.pqa_agent import run_pqa_checks
from agents.data_auditor import build_data_audit


def load_example(name):
    return json.loads((ROOT / "data" / "examples" / name).read_text())


def test_ttek_starter_usable_data_not_fail():
    audit = load_example("TTEK.audit.json")
    data_audit = build_data_audit(
        ticker="TTEK",
        model_id="M13",
        current_price=51.0,
        price_as_of="2026-05-14",
        benchmark_etf=["PHO", "PIO"],
        buy_zone_low=48.0,
        buy_zone_high=55.0,
        eps_guidance_midpoint=3.0,
    )
    dashboard = {"status": "Starter", "freshness": "Fresh"}

    report = run_pqa_checks(audit, data_audit, dashboard)

    assert report["severity"] in ["Pass", "Warning"]
    assert report["passed"] is True


def test_erii_wait_guidance_withdrawn_not_top_candidate_passes():
    audit = load_example("ERII.audit.json")
    data_audit = {
        "valuation_status": "Unreliable - Guidance Withdrawn",
        "current_price": 12.0,
        "stale_price": False,
        "benchmark_status": "Present",
    }
    dashboard = {"status": "Risk-Blocked", "freshness": "Fresh"}

    report = run_pqa_checks(audit, data_audit, dashboard)

    assert report["severity"] == "Pass"
    assert report["failures"] == []


def test_erii_guidance_withdrawn_buy_fails():
    audit = load_example("ERII.audit.json")
    audit["decision"] = "Buy"
    data_audit = {
        "valuation_status": "Unreliable - Guidance Withdrawn",
        "current_price": 12.0,
        "stale_price": False,
        "benchmark_status": "Present",
    }
    dashboard = {"status": "Top Candidate", "freshness": "Fresh"}

    report = run_pqa_checks(audit, data_audit, dashboard)

    assert report["severity"] == "Fail"
    assert "guidance_withdrawn_blocks_buy" in report["failures"]


def test_missing_current_price_starter_fails():
    audit = load_example("TTEK.audit.json")
    data_audit = {"current_price": None, "stale_price": False, "benchmark_status": "Present", "valuation_status": "Computed"}

    report = run_pqa_checks(audit, data_audit, {"status": "Starter", "freshness": "Fresh"})

    assert "missing_current_price_blocks_action" in report["failures"]


def test_stale_price_starter_fails():
    audit = load_example("TTEK.audit.json")
    data_audit = {"current_price": 50.0, "stale_price": True, "benchmark_status": "Present", "valuation_status": "Computed"}

    report = run_pqa_checks(audit, data_audit, {"status": "Starter", "freshness": "Stale"})

    assert "stale_price_blocks_action" in report["failures"]


def test_missing_benchmark_starter_fails():
    audit = load_example("TTEK.audit.json")
    data_audit = {"current_price": 50.0, "stale_price": False, "benchmark_status": "Missing", "valuation_status": "Computed"}

    report = run_pqa_checks(audit, data_audit, {"status": "Starter", "freshness": "Fresh"})

    assert "missing_benchmark_blocks_action" in report["failures"]


def test_high_risk_core_fails():
    audit = load_example("TTEK.audit.json")
    audit["risk_score"] = 8
    audit["position_class"] = "Core Heavy Buy"

    report = run_pqa_checks(audit, {}, {"status": "Starter", "freshness": "Fresh"})

    assert "high_risk_cannot_be_core" in report["failures"]


def test_dashboard_top_candidate_with_wait_fails():
    audit = load_example("ERII.audit.json")
    dashboard = {"status": "Top Candidate", "freshness": "Fresh"}

    report = run_pqa_checks(audit, {"stale_price": False}, dashboard)

    assert "blocked_name_cannot_be_top_candidate" in report["failures"]
