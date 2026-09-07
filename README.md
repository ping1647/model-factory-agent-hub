# Model Factory Agent Hub

A full-automation research and dashboard system for Ping's Investing Model Factory.

## Goal

Automate the workflow from watchlist → source collection → source reading → data audit → risk audit → model learning → dashboard update → human approval.

This system is decision-support only. It must never execute buy/sell orders.

## Current reference cases

- TTEK = Final Audit V1 / Starter / Core-Satellite
- ERII = Final Audit V1 / Wait / Risk-Blocked
- SOFI = Final Audit V1 / Starter / High-Beta Satellite

## Manual Batch Workflow (v0.1)

Use `python scripts/run_manual_batch.py` to run a deterministic local batch using:
- active tickers from `data/watchlists/master_watchlist.json`
- local market seed inputs from `data/market_inputs/manual_batch_market_inputs.json`
- local base audits (when available) from `data/examples/*.audit.json`

The script persists run records under `data/runs/`, exports `data/dashboard/latest_dashboard_data.json`, and mirrors the same dashboard payload to `app/dashboard/public/dashboard_data.json` for frontend use.

## Offline Quality Score Validation

Use the standalone validator to reconcile reported scores with the disclosed formula
`expected_quality = 0.6 * business_model + 0.4 * quant_quality`:

```bash
python scripts/validate_quality_scores.py input.csv --output validation.json --tolerance 1e-8
```

CSV input requires `ticker`, `business_model`, `quant_quality`, and
`reported_quality`; `sheet_row` is optional. JSON may be a row array or an object
with a `rows` array and optional `processing_status`. Missing, nonnumeric,
non-finite, mismatched, and empty inputs fail score validation. Passing score
validation does **not** mean an investment decision is ready: evidence, thesis,
valuation, and other QA gates remain separate. An input status such as `COMPLETE`
is retained as processing metadata and cannot override a validation failure. The
validator does not alter reported scores.

This is currently an offline QA component only. No confirmed generator for the
weekly 40-stock workbook is present, so the validator is not yet connected to the
Sunday report-generation path.

The shared definitions and integration plan are documented in
[`docs/WEEKLY_STOCK_SELECTION_SPEC.md`](docs/WEEKLY_STOCK_SELECTION_SPEC.md) and
[`docs/END_TO_END_PILOT_PLAN.md`](docs/END_TO_END_PILOT_PLAN.md).

Run the synthetic end-to-end readiness/export check with one command:

```bash
python scripts/build_synthetic_report.py data/synthetic/SYNTHETIC_DEMO.json
```

It writes local-only JSON, XLSX, and PDF artifacts under
`artifacts/synthetic_demo/`. The fixture is explicitly synthetic and is not a
Weekly40 production run. Delivery remains failed while any reopen/render check is
failed, unknown, or marked as a stub. In the current dependency-limited
environment, the XLSX contains Thai labels, while visual Thai PDF rendering is
explicitly reported as a delivery-QA stub rather than falsely marked as passed.
