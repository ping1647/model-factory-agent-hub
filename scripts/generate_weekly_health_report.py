"""Generate a deterministic weekly governance and data-health report.

This script never changes model weights and never emits an automatic buy signal.
Missing, stale, contradictory, or unverified inputs are blocked or routed to review.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY = "data/registry/model_registry.json"
DEFAULT_WATCHLIST = "data/watchlists/master_watchlist.json"
DEFAULT_MARKET_INPUTS = "data/market_inputs/manual_batch_market_inputs.json"
DEFAULT_PROVENANCE = "data/governance/source_provenance.json"
DEFAULT_CONTRADICTIONS = "data/governance/contradiction_log.json"
DEFAULT_EXAMPLES_DIR = "data/examples"
DEFAULT_OUTPUT = "data/reports/latest_weekly_health_report.json"


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def age_days(value: str | None, as_of: date) -> int | None:
    parsed = parse_iso_date(value)
    return None if parsed is None else (as_of - parsed).days


def build_report(
    *,
    registry: dict[str, Any],
    watchlist: list[dict[str, Any]],
    market_inputs: dict[str, Any],
    provenance: dict[str, Any],
    contradictions: dict[str, Any],
    examples_dir: str | Path,
    as_of: date,
) -> dict[str, Any]:
    provenance_by_ticker = {
        str(entry.get("ticker", "")).upper(): entry
        for entry in provenance.get("entries", [])
    }
    contradiction_tickers = {
        str(item.get("ticker", "")).upper()
        for item in contradictions.get("open_items", [])
        if item.get("material", True)
    }
    active_items = [
        item for item in watchlist
        if str(item.get("status", "")).lower() == "active"
    ]

    ticker_health: list[dict[str, Any]] = []
    for item in active_items:
        ticker = str(item.get("ticker", "")).upper()
        model_id = str(item.get("model_id", "")).upper()
        inputs = market_inputs.get(ticker, {})
        source = provenance_by_ticker.get(ticker)
        blockers: list[str] = []
        review_items: list[str] = []

        price_age = age_days(inputs.get("price_as_of"), as_of)
        if inputs.get("current_price") is None:
            blockers.append("missing_current_price")
        if price_age is None:
            blockers.append("missing_or_invalid_price_timestamp")
        elif price_age > 7:
            blockers.append("stale_price_over_7_days")

        buy_zone_age = age_days(inputs.get("buy_zone_as_of"), as_of)
        if inputs.get("buy_zone_low") is None or inputs.get("buy_zone_high") is None:
            review_items.append("missing_buy_zone")
        elif buy_zone_age is None:
            review_items.append("missing_or_invalid_buy_zone_timestamp")
        elif buy_zone_age > 30:
            blockers.append("stale_buy_zone_over_30_days")

        if bool(inputs.get("guidance_withdrawn", False)):
            blockers.append("guidance_withdrawn")

        if source is None or source.get("verification_status") != "verified":
            blockers.append("unverified_source_provenance")

        if ticker in contradiction_tickers:
            blockers.append("unresolved_material_contradiction")

        if inputs.get("eps_guidance_midpoint") is None:
            review_items.append("eps_valuation_basis_unavailable")

        base_audit_exists = (Path(examples_dir) / f"{ticker}.audit.json").exists()
        if not base_audit_exists:
            review_items.append("missing_base_audit")

        if blockers:
            status = "Blocked"
        elif review_items:
            status = "Needs Audit"
        else:
            status = "Healthy"

        ticker_health.append({
            "ticker": ticker,
            "model_id": model_id,
            "status": status,
            "blockers": sorted(set(blockers)),
            "review_items": sorted(set(review_items)),
            "price_as_of": inputs.get("price_as_of"),
            "price_age_days": price_age,
            "buy_zone_as_of": inputs.get("buy_zone_as_of"),
            "buy_zone_age_days": buy_zone_age,
            "base_audit_exists": base_audit_exists,
            "source_verification_status": None if source is None else source.get("verification_status"),
            "automatic_buy_signal": false,
        })

    health_by_model: dict[str, list[dict[str, Any]]] = {}
    for item in ticker_health:
        health_by_model.setdefault(item["model_id"], []).append(item)

    model_health: list[dict[str, Any]] = []
    for model in registry.get("models", []):
        model_id = model.get("model_id")
        members = health_by_model.get(model_id, [])
        if members:
            states = {member["status"] for member in members}
            if "Blocked" in states:
                weekly_status = "Blocked"
            elif "Needs Audit" in states:
                weekly_status = "Needs Audit"
            else:
                weekly_status = "Healthy"
        else:
            weekly_status = model.get("status", "Unknown")
        model_health.append({
            "model_id": model_id,
            "name": model.get("name"),
            "level": model.get("level"),
            "registry_status": model.get("status"),
            "weekly_status": weekly_status,
            "active_tickers": [member["ticker"] for member in members],
            "progress_pct": model.get("progress_pct"),
            "test_case_count": model.get("test_case_count"),
            "decision_support_only": True,
        })

    status_counts = Counter(item["status"] for item in ticker_health)
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "as_of": as_of.isoformat(),
        "governance": {
            "decision_support_only": True,
            "automatic_buy_signals_allowed": False,
            "model_weights_changed": False,
            "default_missing_data_action": "Block or Needs Audit",
        },
        "summary": {
            "active_ticker_count": len(ticker_health),
            "healthy_count": status_counts.get("Healthy", 0),
            "needs_audit_count": status_counts.get("Needs Audit", 0),
            "blocked_count": status_counts.get("Blocked", 0),
        },
        "ticker_health": ticker_health,
        "model_health": model_health,
        "legacy_packs": registry.get("legacy_packs", []),
        "excluded_models": registry.get("excluded_models", []),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate weekly model governance health report")
    parser.add_argument("--registry", default=DEFAULT_REGISTRY)
    parser.add_argument("--watchlist", default=DEFAULT_WATCHLIST)
    parser.add_argument("--market-inputs", default=DEFAULT_MARKET_INPUTS)
    parser.add_argument("--provenance", default=DEFAULT_PROVENANCE)
    parser.add_argument("--contradictions", default=DEFAULT_CONTRADICTIONS)
    parser.add_argument("--examples-dir", default=DEFAULT_EXAMPLES_DIR)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--as-of", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    as_of = parse_iso_date(args.as_of) if args.as_of else date.today()
    if as_of is None:
        raise SystemExit("--as-of must be YYYY-MM-DD")

    report = build_report(
        registry=load_json(args.registry),
        watchlist=load_json(args.watchlist),
        market_inputs=load_json(args.market_inputs),
        provenance=load_json(args.provenance),
        contradictions=load_json(args.contradictions),
        examples_dir=args.examples_dir,
        as_of=as_of,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"weekly_health_report: {output}")
    print(f"summary: {report['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
