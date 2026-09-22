# Weekly US Stock Selection: Shared QA Specification

## Purpose and boundary

The weekly system is decision support for finding durable US businesses whose
current price may offer attractive risk-adjusted return. It must keep business
quality, price-dependent opportunity, and analysis reliability separate. It does
not place trades; a human must approve every investment action.

This specification is a contract for future components. It does not prove that
the historical W36 workbook generator or an external ChatGPT task is connected to
this repository.

## Three independent assessment dimensions

1. **Quality**: durability of the business, demand, moat, execution, balance-sheet
   resilience, and per-share risks. Price is not the primary driver.
2. **Opportunity**: expected risk-adjusted return at today's price, including
   valuation, downside, benchmark-relative potential, and entry conditions.
3. **Analysis Reliability**: source quality, freshness, completeness,
   reproducibility, contradictions, and confidence in estimates.

A high result in one dimension must not repair or conceal a failure in another.
Dashboards and exports must retain all three dimensions rather than collapse them
into an unexplained single score.

## Existing formulas and proposed rules

| Item | Status | Requirement |
|---|---|---|
| Quality reconciliation | **Implemented** | The offline validator checks `0.6 * business_model + 0.4 * quant_quality`, with default tolerance `1e-8`. This checks consistency only. |
| Forward P/E | **Implemented, limited** | The current data auditor can compute `current_price / eps_guidance_midpoint`; it is not a complete valuation model. |
| Quality component construction | **Not verified** | No confirmed repository generator explains how business-model or quantitative inputs are produced or adjusted. |
| Opportunity formula/weights | **Proposed, not defined** | Do not introduce weights until methodology, overlap tests, and human approval are recorded. |
| Analysis Reliability formula/weights | **Proposed, not defined** | Existing blockers can inform it, but no composite score is approved. |
| Investment threshold and sizing | **Proposed, not defined** | Formula consistency alone must never imply a buy, sizing, or decision readiness. |

Every proposed formula must be labelled `PROPOSED` in output until approved. Its
version, components, weights, units, and effective date must be recorded.

## Time, evidence, and revalidation

- Each run has a **latest-available as-of cutoff**. Only information publicly
  available by that cutoff may affect the result.
- Every fact records three dates where applicable: **data date** (period the fact
  describes), **publication date**, and **verification date**.
- Previously collected evidence must be revalidated for superseding filings,
  restatements, corrected releases, changed guidance, broken links, and material
  contradictions. Reuse is allowed only with provenance and a fresh revalidation
  outcome.
- The run must disclose timezone and cutoff. Evidence published after cutoff is
  reserved for the next run, not backfilled silently.

## Historical calculations

- A historical window must define endpoints, observation frequency, adjusted or
  unadjusted prices, corporate-action handling, and benchmark convention.
- If the full requested window is unavailable, label the metric `N/A`; do not
  substitute a shorter window while retaining a 3-year or 5-year label.
- CAGR is `N/A` when endpoints are absent/non-finite, the elapsed period is
  insufficient, or the calculation is mathematically undefined. The reason and
  available coverage must accompany `N/A`.

## Valuation and expected return

- **Fair value today**, **terminal value**, and **expected return** are separate
  outputs. Terminal value must not be displayed as today's fair value.
- Expected return states horizon, distributions/cash flows, dilution, downside,
  and benchmark. It must not be inferred merely from price versus fair value.
- Every valuation must be reconstructable from stored inputs and adjustments:
  source, date, unit, currency, share basis, normalization, formula, scenario,
  and rounding. Unexplained plugs or hidden adjustments fail valuation QA.
- Missing valuation inputs remain missing; they are never replaced with zero.

## Double-counting control

Maintain a factor-to-economic-driver map before combining scores. Factors that
share the same causal exposure—for example rates affecting discount rate,
financing cost, and demand—must be identified. Either allocate the exposure once,
orthogonalize it, or document and cap the intentional overlap. Opportunity must
not reward cheap valuation twice through both a valuation component and a second
proxy derived from that same valuation.

## User-facing statuses and transition conditions

| Thai status | Meaning | Minimum condition to change |
|---|---|---|
| `ศึกษาต่อ` | Initial research is incomplete but viable. | Required sources and model-specific factors become sufficiently complete for thesis and valuation QA. |
| `รอราคา` | Thesis/reliability pass, but current opportunity or entry condition does not. | Fresh price enters an approved valuation/return range without a new blocker. |
| `รอหลักฐาน` | A material evidence, provenance, freshness, or contradiction gap blocks judgment. | Missing evidence is verified and contradictions are resolved or explicitly bounded. |
| `ผ่านเงื่อนไขพิจารณาลงทุน` | All required gates pass; this permits human consideration, not execution. | Downgrade immediately if evidence, thesis, valuation, risk, or freshness fails. |
| `งดพิจารณาซื้อขณะนี้` | Thesis is broken or current risk/reward is unacceptable. | A documented thesis-changing fact or materially improved risk/reward triggers a full re-review. |

Each stock output must list its current status, blockers, and concrete transition
triggers. Vague triggers such as “monitor” are insufficient.

## Lifecycle gates

1. **Processing**: jobs read and emit the expected artifacts. `COMPLETE` belongs
   only here and says nothing about analytical correctness.
2. **Data QA**: schema, types, finite values, freshness, windows, provenance,
   reconciliation, and missing-data checks.
3. **Thesis/Valuation QA**: model-specific thesis, risk challenge, valuation
   reconstruction, scenario logic, expected return, and double-counting review.
4. **Delivery QA**: PDF/Excel/dashboard artifacts open successfully, agree with
   validated data, show blockers, and contain no contradictory actionable text.

Passing an earlier gate never implies passing a later one.

## Stock-level versus report-level failures

- A stock-level issue blocks that stock and records its reason without silently
  removing it from coverage.
- A report-level issue blocks the entire report when it can affect shared logic or
  multiple names: wrong formula/version, corrupt or partial universe, invalid
  cutoff, common-source failure, systematic date-window error, export mismatch,
  or an unreconciled aggregate.
- Any failed required gate prohibits an actionable `Buy` message for the affected
  stock. A report-level critical failure prohibits actionable buys throughout the
  report, even when processing says `COMPLETE`.

