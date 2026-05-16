# Web MVP Scaffold v0.1

Static React + Vite dashboard scaffold for the future Model Factory web app.

## Scope

- No database.
- No login.
- No external API calls.
- No portfolio or account connectivity.

## Dashboard Data Source

The dashboard now reads data from generated JSON output:

- Primary path (GitHub Pages): `/model-factory-agent-hub/dashboard_data.json`
- Local fallback path: `/dashboard_data.json`
- Static fallback data in code: `src/sampleDashboardData.js` (used only if fetch fails)

Default generated file:

- `public/dashboard_data.json`

Expected JSON shape (aligned to `agents/dashboard_data_builder.py`):

- `summary`
- `command_center`
- `buy_zone_board`
- `risk_blocked`
- `needs_audit`
- `failed`
- `warnings`
- `latest_agent_runs_placeholder`

## Data Conventions in This MVP

- `pipeline_status`: `Pass`, `Warning`, `Fail`, `Needs Audit`
- `decision`: `Buy`, `Starter`, `Wait`, `Risk-Blocked`, `Avoid`
- `risk_score`: 1-10 scale
- `blockers`: array of blocker keys (renders as `None` when empty)

## Included Boards

- Summary cards: total, pass, warning, fail, needs audit, risk blocked
- Command Center
- Buy Zone Board
- Risk-Blocked
- Needs Audit
- Failed
- Warnings

## Local Run

```bash
npm install
npm run dev
```

## Build Preview

```bash
npm run build
npm run preview
```

## GitHub Pages Deployment

This dashboard deploys from GitHub Actions on pushes to `main` via `.github/workflows/deploy-dashboard-pages.yml`.

- Vite base path is set to `/model-factory-agent-hub/` for Pages hosting.
- The workflow builds `app/dashboard` and deploys `app/dashboard/dist` to GitHub Pages.

## Notes

This is an MVP presentation layer intended for dashboard UX iteration.
All trading decisions remain human-approved.


## Compatibility Notes (Generated JSON v0.2)

The UI supports both legacy and generated summary keys:

- `total` or `total_count`
- `pass` or `pass_count`
- `warning` or `warning_count`
- `fail` or `fail_count`
- `needs_audit` or `needs_audit_count`
- `risk_blocked` or `risk_blocked_count`

Command Center ticker lists (`top_candidates`, `blocked_names`, `needs_review`) may contain either ticker strings or stock objects with a `ticker` field; both shapes are rendered safely.

If `generated_at` is missing, the header shows `Generated: latest dashboard_data.json`.
