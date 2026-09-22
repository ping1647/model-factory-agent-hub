"""Synthetic gate aggregation and export-path tests."""

from __future__ import annotations

import json
from pathlib import Path

from agents.report_readiness import aggregate_report_readiness, apply_delivery_qa
from agents.synthetic_report_exporter import export_pdf, export_xlsx, inspect_pdf, inspect_xlsx

ROOT = Path(__file__).resolve().parents[1]


def load_demo():
    return json.loads((ROOT / "data/synthetic/SYNTHETIC_DEMO.json").read_text(encoding="utf-8"))


def test_stock_failures_and_unknown_stub_fail_closed():
    report = aggregate_report_readiness(load_demo())
    stocks = {stock["ticker"]: stock for stock in report["stocks"]}

    assert stocks["SYN-A"]["analytical_gates_passed"] is True
    assert stocks["SYN-A"]["actionable_buy"] is False
    assert stocks["SYN-C"]["gates"]["data_qa"] == "FAIL"
    assert "quality_score_validation_failed" in stocks["SYN-D"]["blockers"]
    assert stocks["SYN-E"]["gates"]["thesis_valuation_qa"] == "FAIL"
    assert report["actionable_buys_allowed"] is False
    assert report["production_ready"] is False


def test_shared_critical_failure_blocks_every_stock():
    dataset = load_demo()
    dataset["shared_checks"].append({"code": "shared_formula_corrupt", "result": "FAIL"})

    report = aggregate_report_readiness(dataset)

    assert report["shared_critical_status"] == "FAIL"
    assert all("shared_formula_corrupt" in stock["blockers"] for stock in report["stocks"])
    assert all(stock["actionable_buy"] is False for stock in report["stocks"])


def test_missing_shared_gate_is_unknown_and_fails_closed():
    dataset = load_demo()
    dataset.pop("shared_checks")

    report = aggregate_report_readiness(dataset)

    assert report["shared_critical_status"] == "UNKNOWN"
    assert report["report_validation_passed"] is False
    assert report["actionable_buys_allowed"] is False


def test_malformed_structured_finding_fails_instead_of_crashing():
    dataset = load_demo()
    dataset["shared_checks"] = ["not-a-structured-check"]

    report = aggregate_report_readiness(dataset)

    assert report["shared_critical_status"] == "FAIL"
    assert report["shared_critical_blockers"] == ["invalid_finding"]


def test_excel_and_pdf_reopen_against_same_validated_dataset(tmp_path):
    report = aggregate_report_readiness(load_demo())
    xlsx = tmp_path / "SYNTHETIC_DEMO.xlsx"
    pdf = tmp_path / "SYNTHETIC_DEMO.pdf"

    export_xlsx(report, xlsx)
    export_pdf(report, pdf)
    checks = [inspect_xlsx(xlsx, report), *inspect_pdf(pdf, report)]
    report = apply_delivery_qa(report, checks)

    assert checks[0]["result"] == "PASS"
    assert checks[1]["result"] == "PASS"
    assert checks[2]["result"] == "STUB"
    assert report["gates"]["delivery_qa"]["status"] == "FAIL"
    assert report["delivery_verified"] is False
    assert report["production_ready"] is False
