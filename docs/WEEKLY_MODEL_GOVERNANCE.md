# Weekly Model Governance

## Purpose

Keep Investing Model Factory data fresh without retraining on short-term noise. All L4 models remain risk-restricted decision-support only and must never be treated as automatic buy signals.

## Cadence

- Weekly, Sunday 15:00 Asia/Bangkok: refresh health, freshness, contradiction, risk, and dashboard state. Model weights do not change.
- Monthly: recalibrate valuation bands and thresholds after reproducible valuation checks.
- Quarterly or after a major earnings cycle: consider retraining factor weights only after benchmark alpha, drawdown, and false-signal review.
- Event-driven: immediately block or review on guidance withdrawal, restatement, leadership change, material dilution, regulatory shock, or thesis-breaking execution failure.

## Weekly pipeline

1. Load authoritative model registry.
2. Validate active watchlist inputs.
3. Check price freshness; price older than seven days is blocked.
4. Check buy-zone freshness; a valuation band older than 30 days is blocked.
5. Require source provenance for verified facts.
6. Block unresolved material contradictions.
7. Require a base audit before a ticker can become Healthy.
8. Generate the weekly health report.
9. Run the deterministic watchlist batch.
10. Publish outputs for human review only.

## Default decisions

- Missing or unverified data: Blocked or Needs Audit.
- Guidance withdrawn: Blocked.
- Material source contradiction: Blocked.
- No compatible valuation basis: Needs Audit.
- No base audit: Needs Audit.
- No verified benchmark evidence: no L5 promotion.

## Registry rules

- Core registry is M1 through M14.
- Legacy M2 AI Data Center / Compute Infrastructure Pack remains separate.
- Legacy M3 Digital Commerce / Marketplace / AdTech Pack remains separate.
- M15 and M16 are excluded and may not be trained until explicitly recovered and defined.
- Unknown progress, test counts, win rates, or alpha must be stored as null rather than estimated.

## Current limitation

The weekly workflow validates and blocks stale or unsupported inputs, but it does not yet fetch licensed live market data or automatically ingest company filings. Until source collectors are implemented and credentials are configured, weekly runs may correctly return Blocked rather than fabricate freshness.

## Next implementation batches

1. Attach primary-source provenance to all active tickers.
2. Add provider-backed price and benchmark collection.
3. Add base audits for NVDA, HIMS, and VST.
4. Add valuation adapters for revenue, EBITDA, and FCF guidance.
5. Add benchmark alpha, drawdown, and false-signal measurement.
6. Re-enable paused models one at a time after their source collector and tests pass.
