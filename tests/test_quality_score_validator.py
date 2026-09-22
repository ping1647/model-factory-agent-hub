"""Tests use synthetic examples, not extracted report data."""

from __future__ import annotations

import json

import pytest

from agents.quality_score_validator import load_quality_rows, validate_quality_scores


def synthetic_row(**overrides):
    row = {
        "ticker": "TEST",
        "sheet_row": 2,
        "business_model": 8.0,
        "quant_quality": 5.0,
        "reported_quality": 6.8,
    }
    row.update(overrides)
    return row


def test_matching_score_passes_but_is_not_investment_decision_ready():
    report = validate_quality_scores([synthetic_row()])

    assert report["processing_completed"] is True
    assert report["validation_passed"] is True
    assert report["decision_ready"] is False
    assert report["decision_readiness_blockers"] == [
        "requires_evidence_thesis_and_valuation_qa"
    ]
    assert report["rows"][0]["status"] == "PASS"
    assert report["rows"][0]["difference"] == pytest.approx(0.0)


def test_mismatched_score_fails_without_silent_correction():
    report = validate_quality_scores([synthetic_row(reported_quality=7.1)])

    assert report["validation_passed"] is False
    assert report["decision_ready"] is False
    assert "quality_score_validation_failed" in report["decision_readiness_blockers"]
    assert report["rows"][0]["reported_quality"] == 7.1
    assert report["rows"][0]["expected_quality"] == pytest.approx(6.8)
    assert report["rows"][0]["status"] == "FAIL"


@pytest.mark.parametrize("field,value", [
    ("business_model", ""),
    ("quant_quality", "not-a-number"),
    ("reported_quality", float("inf")),
])
def test_missing_nonnumeric_and_nonfinite_values_fail(field, value):
    report = validate_quality_scores([synthetic_row(**{field: value})])

    result = report["rows"][0]
    assert result["status"] == "FAIL"
    assert f"invalid_or_missing_{field}" in result["errors"]
    assert result["expected_quality"] is None
    assert report["decision_ready"] is False


def test_empty_input_is_not_valid_or_decision_ready():
    report = validate_quality_scores([])

    assert report["processing_completed"] is True
    assert report["row_count"] == 0
    assert report["validation_passed"] is False
    assert report["decision_ready"] is False


def test_complete_input_status_cannot_override_critical_failure(tmp_path):
    path = tmp_path / "synthetic.json"
    path.write_text(json.dumps({
        "processing_status": "COMPLETE",
        "rows": [synthetic_row(reported_quality=9.0)],
    }), encoding="utf-8")

    rows, status = load_quality_rows(path)
    report = validate_quality_scores(rows, input_processing_status=status)

    assert report["input_processing_status"] == "COMPLETE"
    assert report["processing_completed"] is True
    assert report["critical_failure_count"] == 1
    assert report["validation_passed"] is False
    assert report["decision_ready"] is False


def test_csv_input_is_supported(tmp_path):
    path = tmp_path / "synthetic.csv"
    path.write_text(
        "ticker,sheet_row,business_model,quant_quality,reported_quality\n"
        "TEST,2,8,5,6.8\n",
        encoding="utf-8",
    )

    rows, status = load_quality_rows(path)
    report = validate_quality_scores(rows, input_processing_status=status)

    assert report["validation_passed"] is True
