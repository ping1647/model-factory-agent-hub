from agents.dashboard_data_builder import build_dashboard_data


def _result(
    ticker: str,
    pipeline_status: str,
    decision: str = "Buy",
    buy_zone_status: str = "Out of Buy Zone",
    dashboard_status: str = "Buy",
) -> dict:
    return {
        "ticker": ticker,
        "model_id": "M13",
        "pipeline_status": pipeline_status,
        "data_audit": {
            "buy_zone_status": buy_zone_status,
            "valuation_status": "Fair",
        },
        "risk_adjusted_audit": {
            "decision": decision,
            "risk_score": 4,
            "position_class": "Starter",
        },
        "dashboard_card": {"status": dashboard_status},
        "blockers": [],
        "next_action": "review",
    }


def test_ttek_in_buy_zone_pass_in_top_candidates():
    data = build_dashboard_data(
        [_result("TTEK", "Pass", decision="Buy", buy_zone_status="In Buy Zone", dashboard_status="Buy")]
    )

    assert any(item["ticker"] == "TTEK" for item in data["buy_zone_board"])
    assert any(item["ticker"] == "TTEK" for item in data["command_center"]["top_candidates"])


def test_erii_wait_is_risk_blocked_not_top_candidate():
    data = build_dashboard_data(
        [_result("ERII", "Pass", decision="Wait", buy_zone_status="In Buy Zone", dashboard_status="Risk-Blocked")]
    )

    assert any(item["ticker"] == "ERII" for item in data["risk_blocked"])
    assert any(item["ticker"] == "ERII" for item in data["command_center"]["blocked_names"])
    assert not any(item["ticker"] == "ERII" for item in data["command_center"]["top_candidates"])


def test_missing_current_price_fail_in_failed_and_needs_review():
    data = build_dashboard_data([_result("TTEK", "Fail", decision="Wait")])

    assert any(item["ticker"] == "TTEK" for item in data["failed"])
    assert any(item["ticker"] == "TTEK" for item in data["command_center"]["needs_review"])


def test_no_base_audit_needs_audit_bucketed():
    result = _result("SOFI", "Needs Audit")
    result["risk_adjusted_audit"] = None
    result["dashboard_card"] = None

    data = build_dashboard_data([result])

    assert any(item["ticker"] == "SOFI" for item in data["needs_audit"])


def test_warning_pipeline_in_warnings_and_needs_review():
    data = build_dashboard_data([_result("ABC", "Warning")])

    assert any(item["ticker"] == "ABC" for item in data["warnings"])
    assert any(item["ticker"] == "ABC" for item in data["command_center"]["needs_review"])
