"""Deterministic Data Auditor v0.1 for input readiness checks."""

from __future__ import annotations

from datetime import date
from typing import Any


def _parse_iso_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def build_data_audit(
    ticker: str,
    model_id: str,
    current_price: float | None,
    price_as_of: str | None,
    benchmark_etf: list[str],
    buy_zone_low: float | None = None,
    buy_zone_high: float | None = None,
    eps_guidance_midpoint: float | None = None,
    guidance_withdrawn: bool = False,
    max_price_age_days: int = 7,
) -> dict[str, Any]:
    blockers: list[str] = []

    parsed_price_date = _parse_iso_date(price_as_of)
    stale_price = False

    if current_price is None:
        blockers.append("missing_current_price")

    if price_as_of is None:
        blockers.append("missing_price_timestamp")
    elif parsed_price_date is None:
        blockers.append("invalid_price_timestamp")
    else:
        age_days = (date.today() - parsed_price_date).days
        if age_days > max_price_age_days:
            stale_price = True
            blockers.append("stale_price")

    if not benchmark_etf:
        blockers.append("missing_benchmark")

    if buy_zone_low is None or buy_zone_high is None:
        buy_zone_status = "Missing Buy Zone"
        gap_to_buy_zone_pct = None
    elif current_price is None:
        buy_zone_status = "Missing Current Price"
        gap_to_buy_zone_pct = None
    elif current_price < buy_zone_low:
        buy_zone_status = "Below Buy Zone"
        gap_to_buy_zone_pct = ((buy_zone_low - current_price) / buy_zone_low) * 100
    elif current_price > buy_zone_high:
        buy_zone_status = "Above Buy Zone"
        gap_to_buy_zone_pct = ((current_price - buy_zone_high) / buy_zone_high) * 100
    else:
        buy_zone_status = "In Buy Zone"
        gap_to_buy_zone_pct = 0.0

    forward_pe = None
    if current_price is not None and eps_guidance_midpoint not in (None, 0):
        forward_pe = current_price / float(eps_guidance_midpoint)

    if guidance_withdrawn:
        valuation_status = "Unreliable - Guidance Withdrawn"
        blockers.append("guidance_withdrawn")
    elif forward_pe is None:
        valuation_status = "Insufficient Data"
    else:
        valuation_status = "Computed"

    benchmark_status = "Present" if benchmark_etf else "Missing"

    if price_as_of is None:
        price_freshness_status = "Missing Price Timestamp"
    elif parsed_price_date is None:
        price_freshness_status = "Invalid Price Timestamp"
    elif stale_price:
        price_freshness_status = "Stale"
    else:
        price_freshness_status = "Fresh"

    data_quality = "Blocked" if blockers else "Usable"

    return {
        "ticker": ticker,
        "model_id": model_id,
        "current_price": current_price,
        "price_as_of": price_as_of,
        "price_freshness_status": price_freshness_status,
        "stale_price": stale_price,
        "benchmark_etf": benchmark_etf,
        "benchmark_status": benchmark_status,
        "buy_zone_low": buy_zone_low,
        "buy_zone_high": buy_zone_high,
        "buy_zone_status": buy_zone_status,
        "gap_to_buy_zone_pct": gap_to_buy_zone_pct,
        "eps_guidance_midpoint": eps_guidance_midpoint,
        "forward_pe": forward_pe,
        "valuation_status": valuation_status,
        "decision_blockers": sorted(set(blockers)),
        "data_quality": data_quality,
        "next_action": "Resolve decision blockers" if blockers else "Proceed to risk review",
    }
