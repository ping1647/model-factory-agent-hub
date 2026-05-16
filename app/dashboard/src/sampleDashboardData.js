export const sampleDashboardData = {
  generated_at: '2026-05-16T00:00:00Z',
  command_center: {
    mode: 'Static MVP',
    data_source: 'Local mock sample data',
    benchmark: 'SPY',
    note: 'No database, no login, no external APIs. Dashboard data is sample-only.'
  },
  stocks: [
    {
      ticker: 'TTEK',
      model_id: 'M13-WATER',
      pipeline_status: 'ready',
      decision: 'starter',
      risk_score: 32,
      position_class: 'starter',
      buy_zone_status: 'in buy zone',
      valuation_status: 'attractive',
      blockers: 'None critical; continue sizing discipline',
      next_action: 'Confirm latest price timestamp and initiate starter on human approval',
      board: 'top_candidates'
    },
    {
      ticker: 'ERII',
      model_id: 'M13-WATER',
      pipeline_status: 'risk_review',
      decision: 'wait',
      risk_score: 74,
      position_class: 'risk-blocked candidate',
      buy_zone_status: 'near buy zone',
      valuation_status: 'mixed',
      blockers: 'Execution risk and demand-timing uncertainty',
      next_action: 'Resolve thesis risk with updated evidence before any sizing',
      board: 'risk_blocked'
    },
    {
      ticker: 'SOFI',
      model_id: 'M5-FINTECH',
      pipeline_status: 'warning',
      decision: 'starter',
      risk_score: 61,
      position_class: 'high-beta starter',
      buy_zone_status: 'watchlist range',
      valuation_status: 'fair',
      blockers: 'High beta and macro sensitivity; validate delinquency and funding trend',
      next_action: 'Audit missing data and only proceed with strict risk limits',
      board: 'needs_review'
    }
  ]
};
