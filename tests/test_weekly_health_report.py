from __future__ import annotations

from datetime import date

from scripts.generate_weekly_health_report import build_report


def test_unverified_and_stale_inputs_are_blocked(tmp_path):
    registry = {
        "models": [
            {
                "model_id": "M13",
                "name": "Water and PFAS",
                "level": "L4",
                "status": "active_partial",
                "progress_pct": None,
                "test_case_count": None,
            }
        ],
        "legacy_packs": [],
        "excluded_models": [
            {"model_id": "M15", "status": "excluded_undefined", "allowed_for_training": False},
            {"model_id": "M16", "status": "excluded_undefined", "allowed_for_training": False},
        ],
    }
    watchlist = [{"ticker": "TTEK", "model_id": "M13", "status": "active"}]
    market_inputs = {
        "TTEK": {
            "current_price": 31.58,
            "price_as_of": "2026-07-01",
            "buy_zone_low": 44.0,
            "buy_zone_high": 48.0,
            "buy_zone_as_of": "2026-05-16",
            "eps_guidance_midpoint": 1.54,
            "guidance_withdrawn": False,
        }
    }
    provenance = {
        "entries": [
            {"ticker": "TTEK", "verification_status": "unverified"}
        ]
    }
    contradictions = {"open_items": []}
    (tmp_path / "TTEK.audit.json").write_text("{}", encoding="utf-8")

    report = build_report(
        registry=registry,
        watchlist=watchlist,
        market_inputs=market_inputs,
        provenance=provenance,
        contradictions=contradictions,
        examples_dir=tmp_path,
        as_of=date(2026, 7, 18),
    )

    ticker = report["ticker_health"][0]
    assert ticker["status"] == "Blocked"
    assert "stale_price_over_7_days" in ticker["blockers"]
    assert "stale_buy_zone_over_30_days" in ticker["blockers"]
    assert "unverified_source_provenance" in ticker["blockers"]
    assert ticker["automatic_buy_signal"] is False
    assert report["governance"]["model_weights_changed"] is False


def test_verified_fresh_complete_input_can_be_healthy(tmp_path):
    registry = {
        "models": [
            {
                "model_id": "M13",
                "name": "Water and PFAS",
                "level": "L4",
                "status": "active_partial",
                "progress_pct": None,
                "test_case_count": None,
            }
        ],
        "legacy_packs": [],
        "excluded_models": [],
    }
    watchlist = [{"ticker": "TTEK", "model_id": "M13", "status": "active"}]
    market_inputs = {
        "TTEK": {
            "current_price": 31.58,
            "price_as_of": "2026-07-17",
            "buy_zone_low": 28.0,
            "buy_zone_high": 32.0,
            "buy_zone_as_of": "2026-07-17",
            "eps_guidance_midpoint": 1.54,
            "guidance_withdrawn": False,
        }
    }
    provenance = {
        "entries": [
            {"ticker": "TTEK", "verification_status": "verified"}
        ]
    }
    contradictions = {"open_items": []}
    (tmp_path / "TTEK.audit.json").write_text("{}", encoding="utf-8")

    report = build_report(
        registry=registry,
        watchlist=watchlist,
        market_inputs=market_inputs,
        provenance=provenance,
        contradictions=contradictions,
        examples_dir=tmp_path,
        as_of=date(2026, 7, 18),
    )

    assert report["ticker_health"][0]["status"] == "Healthy"
    assert report["summary"]["healthy_count"] == 1
