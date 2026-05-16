"""Manual deterministic batch runner for GitHub Actions workflow_dispatch."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.batch_runner import load_watchlist, run_and_persist_batch

DEFAULT_WATCHLIST_PATH = "data/watchlists/master_watchlist.json"
DEFAULT_FACTOR_MATRIX_PATH = "data/model_factor_matrix_min.json"
DEFAULT_MARKET_INPUTS_PATH = "data/market_inputs/manual_batch_market_inputs.json"
DEFAULT_RUN_OUTPUT_DIR = "data/runs"
DEFAULT_DASHBOARD_OUTPUT_PATH = "data/dashboard/latest_dashboard_data.json"
DEFAULT_DASHBOARD_PUBLIC_PATH = "app/dashboard/public/dashboard_data.json"
DEFAULT_BASE_AUDITS = ("TTEK", "ERII", "SOFI")


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_run_context(target_models: list[str]) -> dict[str, Any]:
    freshness = {"freshness": "fresh"}
    return {
        "model_registry_master": dict(freshness),
        "model_checkpoint_latest": dict(freshness),
        "changelog_master": dict(freshness),
        "model_factor_matrix": dict(freshness),
        "contradiction_log": dict(freshness),
        "target_models": target_models,
    }


def load_base_audits(examples_dir: str | Path = "data/examples", tickers: tuple[str, ...] = DEFAULT_BASE_AUDITS) -> dict[str, Any]:
    base_audits: dict[str, Any] = {}
    root = Path(examples_dir)
    for ticker in tickers:
        path = root / f"{ticker}.audit.json"
        if path.exists():
            base_audits[ticker] = load_json(path)
    return base_audits


def default_run_id(now: datetime | None = None) -> str:
    value = now or datetime.now(UTC)
    return f"manual-{value.strftime('%Y%m%d-%H%M%S')}"


def default_run_date(now: datetime | None = None) -> str:
    value = now or datetime.now(UTC)
    return value.strftime("%Y-%m-%d")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run manual deterministic watchlist batch")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--run-date", default=None)
    parser.add_argument("--watchlist-path", default=DEFAULT_WATCHLIST_PATH)
    parser.add_argument("--market-inputs-path", default=DEFAULT_MARKET_INPUTS_PATH)
    parser.add_argument("--dashboard-output-path", default=DEFAULT_DASHBOARD_OUTPUT_PATH)
    parser.add_argument("--dashboard-public-path", default=DEFAULT_DASHBOARD_PUBLIC_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    watchlist = load_watchlist(args.watchlist_path)
    model_factor_matrix = load_json(DEFAULT_FACTOR_MATRIX_PATH)
    market_inputs_by_ticker = load_json(args.market_inputs_path)
    base_audits_by_ticker = load_base_audits()

    target_models = sorted({str(item.get("model_id", "")).strip().upper() for item in watchlist if item.get("model_id")})
    run_context = build_run_context(target_models)

    run_id = args.run_id or default_run_id()
    run_date = args.run_date or default_run_date()

    result = run_and_persist_batch(
        watchlist=watchlist,
        run_id=run_id,
        run_date=run_date,
        run_context=run_context,
        model_factor_matrix=model_factor_matrix,
        market_inputs_by_ticker=market_inputs_by_ticker,
        base_audits_by_ticker=base_audits_by_ticker,
        run_output_dir=DEFAULT_RUN_OUTPUT_DIR,
        dashboard_output_path=args.dashboard_output_path,
    )

    dashboard_public_path = Path(args.dashboard_public_path)
    dashboard_public_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(result["dashboard_output_path"], dashboard_public_path)

    statuses = Counter(item.get("pipeline_status", "Unknown") for item in result["pipeline_results"])
    tickers = [item.get("ticker", "") for item in result["pipeline_results"]]

    print(f"run_id: {result['run_id']}")
    print(f"run_date: {result['run_date']}")
    print(f"tickers_processed: {', '.join(tickers)}")
    print(f"pipeline_status_counts: {dict(statuses)}")
    print(f"dashboard_output_path: {result['dashboard_output_path']}")
    print(f"dashboard_public_path: {dashboard_public_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
