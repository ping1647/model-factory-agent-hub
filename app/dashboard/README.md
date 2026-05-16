# Web MVP Scaffold v0.1

Static React + Vite dashboard scaffold for the future Model Factory web app.

## Scope

- No database.
- No login.
- No external API calls.
- No portfolio or account connectivity.
- Uses local sample data only (`src/sampleDashboardData.js`).

## Data Conventions in This MVP

- `pipeline_status`: `Pass`, `Warning`, `Fail`, `Needs Audit`
- `decision`: `Buy`, `Starter`, `Wait`, `Risk-Blocked`, `Avoid`
- `risk_score`: 1-10 scale
- `blockers`: array of blocker keys (renders as `None` when empty)

## Included Boards

- Summary cards: total, pass, warning, fail, needs audit, risk blocked
- Command Center
- Top Candidates
- Risk-Blocked
- Needs Review
- Buy Zone Board (exact `In Buy Zone` matches)

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

## Notes

This is an MVP presentation layer intended for dashboard UX iteration.
All trading decisions remain human-approved.
