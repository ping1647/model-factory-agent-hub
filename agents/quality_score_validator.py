"""Offline reconciliation for reported quality scores."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = ("ticker", "business_model", "quant_quality", "reported_quality")


def _finite_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def load_quality_rows(path: str | Path) -> tuple[list[Any], str | None]:
    """Load rows and an optional declared processing status from CSV or JSON."""
    source = Path(path)
    suffix = source.suffix.lower()
    if suffix == ".csv":
        with source.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle)), None
    if suffix == ".json":
        payload = json.loads(source.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return payload, None
        if isinstance(payload, dict) and isinstance(payload.get("rows"), list):
            status = payload.get("processing_status")
            return payload["rows"], None if status is None else str(status)
        raise ValueError("JSON input must be a row array or an object containing a rows array")
    raise ValueError("Input must use a .csv or .json extension")


def validate_quality_scores(
    rows: list[Any],
    *,
    tolerance: float = 1e-8,
    input_processing_status: str | None = None,
) -> dict[str, Any]:
    """Compare reported scores with the disclosed 60/40 quality formula."""
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be a finite, non-negative number")

    results: list[dict[str, Any]] = []
    for index, raw_row in enumerate(rows, start=1):
        row = raw_row if isinstance(raw_row, dict) else {}
        ticker = str(row.get("ticker", "")).strip().upper()
        errors: list[str] = []
        if not ticker:
            errors.append("missing_ticker")

        numbers: dict[str, float] = {}
        for field in REQUIRED_FIELDS[1:]:
            number = _finite_number(row.get(field))
            if number is None:
                errors.append(f"invalid_or_missing_{field}")
            else:
                numbers[field] = number

        expected_quality: float | None = None
        difference: float | None = None
        if not errors:
            expected_quality = 0.6 * numbers["business_model"] + 0.4 * numbers["quant_quality"]
            difference = numbers["reported_quality"] - expected_quality

        passed = not errors and difference is not None and abs(difference) <= tolerance
        results.append({
            "row_number": index,
            "source_row": row.get("sheet_row"),
            "ticker": ticker,
            "business_model": numbers.get("business_model"),
            "quant_quality": numbers.get("quant_quality"),
            "reported_quality": numbers.get("reported_quality"),
            "expected_quality": expected_quality,
            "difference": difference,
            "status": "PASS" if passed else "FAIL",
            "errors": errors,
        })

    validation_passed = bool(results) and all(row["status"] == "PASS" for row in results)
    decision_readiness_blockers = ["requires_evidence_thesis_and_valuation_qa"]
    if not validation_passed:
        decision_readiness_blockers.insert(0, "quality_score_validation_failed")
    return {
        "formula": "0.6 * business_model + 0.4 * quant_quality",
        "tolerance": tolerance,
        "input_processing_status": input_processing_status,
        "processing_completed": True,
        "validation_passed": validation_passed,
        # Formula reconciliation is only one data-QA gate. It cannot establish
        # evidence, thesis, valuation, or investment decision readiness.
        "decision_ready": False,
        "decision_readiness_blockers": decision_readiness_blockers,
        "critical_failure_count": sum(row["status"] == "FAIL" for row in results),
        "row_count": len(results),
        "rows": results,
    }
