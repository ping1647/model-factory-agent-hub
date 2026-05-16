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
      model_id: 'M13',
      pipeline_status: 'Pass',
      decision: 'Starter',
      risk_score: 4,
      position_class: 'Top Candidate',
      buy_zone_status: 'In Buy Zone',
      valuation_status: 'Attractive',
      blockers: [],
      next_action: 'Confirm latest price timestamp and prepare starter sizing for human approval',
      board: 'top_candidates'
    },
    {
      ticker: 'ERII',
      model_id: 'M13',
      pipeline_status: 'Warning',
      decision: 'Wait',
      risk_score: 7,
      position_class: 'Risk-Blocked',
      buy_zone_status: 'Near Buy Zone',
      valuation_status: 'Mixed',
      blockers: ['guidance_withdrawn'],
      next_action: 'Keep risk-blocked until guidance clarity and evidence quality improve',
      board: 'risk_blocked'
    },
    {
      ticker: 'SOFI',
      model_id: 'M5',
      pipeline_status: 'Warning',
      decision: 'Starter',
      risk_score: 7,
      position_class: 'High-Beta Starter',
      buy_zone_status: 'Watchlist Range',
      valuation_status: 'Fair',
      blockers: ['high_beta', 'macro_sensitivity'],
      next_action: 'Complete missing-data audit and retain strict risk controls',
      board: 'needs_review'
    }
  ]
};
