from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from agents.data_auditor import build_data_audit


def test_ttek_in_buy_zone_usable():
    out = build_data_audit(
        ticker="TTEK",
        model_id="M13",
        current_price=26.18,
        price_as_of=date.today().isoformat(),
        benchmark_etf=["PHO"],
        buy_zone_low=26.0,
        buy_zone_high=28.0,
        eps_guidance_midpoint=1.54,
    )
    assert out["buy_zone_status"] == "In Buy Zone"
    assert out["forward_pe"] == 26.18 / 1.54
    assert round(out["forward_pe"], 1) == 17.0
    assert out["data_quality"] == "Usable"


def test_erii_guidance_withdrawn_blocker():
    out = build_data_audit(
        ticker="ERII",
        model_id="M13",
        current_price=8.41,
        price_as_of=date.today().isoformat(),
        benchmark_etf=["PHO"],
        guidance_withdrawn=True,
    )
    assert out["valuation_status"] == "Unreliable - Guidance Withdrawn"
    assert "guidance_withdrawn" in out["decision_blockers"]


def test_missing_price_blocked():
    out = build_data_audit(
        ticker="SOFI",
        model_id="M5",
        current_price=None,
        price_as_of=date.today().isoformat(),
        benchmark_etf=["XLF"],
    )
    assert "missing_current_price" in out["decision_blockers"]
    assert out["data_quality"] == "Blocked"


def test_missing_benchmark_blocker():
    out = build_data_audit(
        ticker="NVDA",
        model_id="M7",
        current_price=100.0,
        price_as_of=date.today().isoformat(),
        benchmark_etf=[],
    )
    assert "missing_benchmark" in out["decision_blockers"]


def test_above_buy_zone_status():
    out = build_data_audit(
        ticker="TTEK",
        model_id="M13",
        current_price=29.5,
        price_as_of=date.today().isoformat(),
        benchmark_etf=["PHO"],
        buy_zone_low=26.0,
        buy_zone_high=28.0,
    )
    assert out["buy_zone_status"] == "Above Buy Zone"
