# Five-Stock End-to-End Pilot and Integration Map

## Current integration map

| Stage | Status | Repository evidence / gap |
|---|---|---|
| Watchlist selection | **มีโค้ดแล้ว** | The manual runner loads active entries from `data/watchlists/master_watchlist.json`. |
| Local market seed loading | **มีโค้ดแล้ว** | `data/market_inputs/manual_batch_market_inputs.json`; it is not a live feed. |
| Model-specific source checklist | **มีโค้ดแล้ว** | `agents/source_collector.py` builds requirements from `data/source_requirements.json`. |
| Filing/news retrieval | **ต้องสร้าง** | Current collector creates requirements but does not retrieve or verify documents. |
| Research summary | **มีโค้ดแล้วแบบโครง** | `agents/research_scout.py` emits a missing-data skeleton, not source-grounded analysis. |
| Price/buy-zone/basic P/E audit | **มีโค้ดแล้วแบบจำกัด** | `agents/data_auditor.py` validates local inputs and can compute forward P/E. |
| Quality formula reconciliation | **มีโค้ดแล้ว** | `agents/quality_score_validator.py`; passing it is only data QA. |
| Full Quality/Opportunity/Reliability calculations | **ต้องสร้าง** | Approved inputs, formulas, versions, and overlap controls are incomplete. |
| Risk and PQA gates | **มีโค้ดแล้วแบบจำกัด** | Existing risk/PQA operate on local base audits and dashboard cards. |
| Run-record and JSON dashboard export | **มีโค้ดแล้ว** | The manual batch persists run JSON and dashboard JSON. |
| Excel/PDF generation and delivery QA | **ต้องสร้าง** | No confirmed W36 workbook generator or tested PDF delivery path was found. |
| Sunday report/task integration | **ยังยืนยันไม่ได้** | No proven link from this repo to the historical workbook or external ChatGPT task. |
| Longbridge, Drive, notification | **ยังยืนยันไม่ได้** | Names or prompts are not credentials, configured integrations, or proof of access. |

The existing weekly health report is governance/data-health output and must not be
treated as the 40-stock report.

## Proposed five-stock pilot (not yet executed)

Use five already-active, cross-model names solely to test the whole path: **TTEK
(M13), ERII (M13), SOFI (M5), NVDA (M7), and VST (M14)**. This selection is a
pilot design, not an investment recommendation and not evidence that fresh data
has been collected.

### 1. Input

- Freeze a run ID, UTC cutoff, ticker/model mapping, benchmark, formula versions,
  and required historical windows.
- Store only licensed/public inputs permitted by their terms; keep private report
  extracts outside tracked/public files.
- Validate schemas, dates, units, currency, split basis, and finite values before
  analysis.

### 2. Evidence

- Primary sources: SEC EDGAR filings (public), company investor-relations earnings
  releases/presentations (generally public), regulator publications, and official
  company announcements.
- Transcripts require a source with explicit access and reuse rights; do not assume
  a paid transcript provider is available.
- Market prices, fundamentals, estimates, and benchmark histories require either
  a public source whose terms permit the use or user-approved licensed access.
  No Longbridge entitlement is assumed.
- Record URL/document ID, issuer, publication date, data date, retrieval time,
  verification time, and the exact claims supported.

### 3. Analysis

- Produce Verified Fact / Model Estimate / Weak Signal / Missing Data sections.
- Apply model-specific factors, include a bear case and kill switches, and keep
  Quality, Opportunity, and Analysis Reliability separate.
- Revalidate reused evidence against sources available by the cutoff.

### 4. Calculations

- Reconcile quality inputs with the implemented 60/40 check without claiming that
  the component-generation method is verified.
- Calculate only approved historical windows and emit `N/A` when coverage is
  insufficient.
- Persist reconstructable valuation scenarios, fair value today, terminal value,
  expected return, benchmark comparison, dilution, and adjustments separately.
- Run and document the economic-driver overlap check before any composite score.

### 5. QA

- Data QA per ticker plus report-level checks for universe completeness, common
  formulas, cutoff, and systematic errors.
- Independent thesis/valuation challenge and actionable-language guardrails.
- A `COMPLETE` processing status cannot override any failed gate.

### 6. PDF/Excel and delivery inspection

- Generate candidate PDF and Excel only after upstream QA artifacts exist.
- Reopen both outputs programmatically, verify sheets/pages, row counts, formulas,
  dates, statuses, blockers, and totals against the validated JSON source.
- Visually inspect representative and failure pages/sheets; confirm no actionable
  buy conflicts with QA.
- Deliver through a user-approved channel only. Google Drive and notifications
  need separately confirmed accounts, scopes, destination, retention, and secrets;
  local file creation alone does not prove delivery.

## What can be done now

- Run synthetic unit and integration tests for score semantics, missing data,
  status propagation, and artifact consistency.
- Define schemas and fixture contracts with no private extracted data.
- Add a dry-run handoff from validated JSON into a non-production exporter using
  clearly synthetic fixtures.
- Inventory existing source requirements and map them to the five pilot models.

## Genuine dependencies

- Human approval of Opportunity and Analysis Reliability methodology, thresholds,
  overlap policy, and status-transition rules.
- Fresh five-stock evidence and market/fundamental history with confirmed rights.
- A confirmed workbook/PDF output contract or generator decision.
- Explicit credentials/scopes only if Drive, broker data, or notification delivery
  is later selected. None is presumed available.
- Confirmation of how, if at all, the Sunday task invokes repository code.

## Smallest next verifiable step

Create a **synthetic, non-production gate-contract integration test** that feeds a
passing quality reconciliation plus explicit failing thesis/valuation gates into
a report-readiness aggregator. Verify that processing can complete while
investment readiness and actionable buys remain blocked. This needs no live data,
external account, schedule change, or private report content.

