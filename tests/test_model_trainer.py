from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from agents.model_trainer import create_training_event, evaluate_training_outcome


def test_create_training_event_defaults():
    event = create_training_event(
        ticker="TTEK",
        model_id="M13",
        decision_date="2026-05-01",
        decision="Starter",
        benchmark_etf=["PHO"],
        thesis_summary="Backlog improving with margin recovery signal.",
        risk_score=4,
        position_class="Starter",
        evidence_quality="High",
        missing_data=["next quarter bookings"],
    )

    assert event["expected_review_windows"] == ["1M", "3M", "6M", "12M"]
    assert event["outcome_status"] == "Pending"
    assert event["rule_update_needed"] is False
    assert event["human_review_required"] is True


def test_ttek_like_starter_is_win():
    event = create_training_event(
        ticker="TTEK",
        model_id="M13",
        decision_date="2026-05-01",
        decision="Starter",
        benchmark_etf=["PHO"],
        thesis_summary="Backlog improving.",
        risk_score=4,
        position_class="Starter",
        evidence_quality="High",
        missing_data=[],
    )

    result = evaluate_training_outcome(event, 12.0, 4.0, -12.0)

    assert result["alpha_pct"] == 8.0
    assert result["outcome_status"] == "Win"


def test_erii_like_kill_switch_forces_loss():
    event = create_training_event(
        ticker="ERII",
        model_id="M13",
        decision_date="2026-05-01",
        decision="Wait",
        benchmark_etf=["PHO"],
        thesis_summary="Guidance risk and execution concerns.",
        risk_score=8,
        position_class="Risk-Blocked",
        evidence_quality="Medium",
        missing_data=["management clarity"],
    )

    result = evaluate_training_outcome(event, 6.0, 2.0, -15.0, kill_switch_triggered=True)

    assert result["outcome_status"] == "Loss"
    assert result["rule_update_needed"] is True


def test_sofi_like_high_beta_is_mixed():
    event = create_training_event(
        ticker="SOFI",
        model_id="M5",
        decision_date="2026-05-01",
        decision="Starter",
        benchmark_etf=["XLF"],
        thesis_summary="Growth remains strong but volatile.",
        risk_score=7,
        position_class="High-Beta Satellite",
        evidence_quality="Medium",
        missing_data=["credit cycle inflection"],
    )

    result = evaluate_training_outcome(event, 10.0, 8.0, -30.0)

    assert result["alpha_pct"] == 2.0
    assert result["outcome_status"] == "Mixed"


def test_underperforming_stock_is_loss():
    event = create_training_event(
        ticker="ABC",
        model_id="M7",
        decision_date="2026-05-01",
        decision="Buy",
        benchmark_etf=["SMH"],
        thesis_summary="AI demand uplift.",
        risk_score=5,
        position_class="Core",
        evidence_quality="High",
        missing_data=[],
    )

    result = evaluate_training_outcome(event, -8.0, 3.0, -10.0)

    assert result["alpha_pct"] == -11.0
    assert result["outcome_status"] == "Loss"
