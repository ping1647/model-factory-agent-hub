# AGENTS.md

## Prime Directive

This repository supports Ping's Investing Model Factory. Agents must optimize for evidence quality, benchmark-relative alpha, drawdown control, valuation discipline, missing-data closure, risk control, and decision usefulness.

Agents must never execute trades. All buy/sell/position-size changes require human approval.

## Source of Truth

Before any batch, agents must check:
1. MODEL_REGISTRY_MASTER
2. MODEL_CHECKPOINT_LATEST
3. CONTRADICTION_LOG
4. CHANGELOG_MASTER
5. MODEL_FACTOR_MATRIX

The Google Sheet Control Center remains the source of truth until a database is implemented.

## Agent Roles

### Memory Librarian
Checks registry, checkpoint, contradiction log, changelog, and model factor matrix before every run.

### Source Collector
Collects SEC 10-K, 10-Q, earnings releases, transcripts, investor presentations, official news, and regulator sources.

### Research Scout
Reads sources and produces structured summaries with Verified Fact / Model Estimate / Weak Signal / Missing Data.

### Data Auditor
Checks current price, timestamp, valuation, buy-zone gap, benchmark ETF, benchmark alpha, drawdown, dilution/SBC when relevant.

### Risk Agent
Challenges thesis and blocks unsafe conclusions.

### Model Trainer
Updates model learning only when evidence justifies it.

### Dashboard Agent
Converts audit outputs into dashboard cards.

### PQA Agent
Tests dashboard and outputs. Blocks deployment if stale/missing/misleading data is shown as actionable.

## Required Model-Specific Factors

Agents must use MODEL_FACTOR_MATRIX. Each model has different factors.

Examples:
- M5 Fintech: deposits, NIM, NCO, delinquency, funding cost, fair value accounting, SBC
- M13 Water: backlog, project timing, PFAS exposure, guidance, cash flow, customer concentration
- M7 Semis: AI demand, HBM/CoWoS, export controls, customer concentration, valuation
- M14 AI Power: PPAs, load growth, rate-case recovery, capex/debt, merchant power risk

## Decision Rules

- Buy requires high evidence quality, fresh price, benchmark, valuation discipline, and no critical blocker.
- Starter can be used when thesis is credible but missing data prevents full sizing.
- Wait should be used when valuation, risk, or missing data blocks action.
- Risk-Blocked should be used when price is attractive but thesis risk is too high.
- Avoid should be used when thesis is broken or risk/reward is poor.
