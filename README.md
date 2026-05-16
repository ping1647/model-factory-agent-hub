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
