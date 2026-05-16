import { sampleDashboardData } from './sampleDashboardData';

const SUMMARY_KEYS = [
  { key: 'total', label: 'Total' },
  { key: 'pass', label: 'Pass' },
  { key: 'warning', label: 'Warning' },
  { key: 'fail', label: 'Fail' },
  { key: 'needs_audit', label: 'Needs Audit' },
  { key: 'risk_blocked', label: 'Risk Blocked' }
];

function computeSummary(stocks) {
  return {
    total: stocks.length,
    pass: stocks.filter((s) => s.pipeline_status === 'ready').length,
    warning: stocks.filter((s) => s.pipeline_status === 'warning').length,
    fail: stocks.filter((s) => s.pipeline_status === 'fail').length,
    needs_audit: stocks.filter((s) => s.pipeline_status === 'warning' || s.pipeline_status === 'risk_review').length,
    risk_blocked: stocks.filter((s) => s.board === 'risk_blocked').length
  };
}

function StockCard({ stock }) {
  return (
    <article className="stock-card">
      <h3>{stock.ticker}</h3>
      <ul>
        <li><span className="field">model_id</span><span>{stock.model_id}</span></li>
        <li><span className="field">pipeline_status</span><span className={`tag ${stock.pipeline_status}`}>{stock.pipeline_status}</span></li>
        <li><span className="field">decision</span><span className="tag decision">{stock.decision}</span></li>
        <li><span className="field">risk_score</span><span>{stock.risk_score}</span></li>
        <li><span className="field">position_class</span><span>{stock.position_class}</span></li>
        <li><span className="field">buy_zone_status</span><span>{stock.buy_zone_status}</span></li>
        <li><span className="field">valuation_status</span><span>{stock.valuation_status}</span></li>
        <li><span className="field">blockers</span><span>{stock.blockers}</span></li>
        <li><span className="field">next_action</span><span>{stock.next_action}</span></li>
      </ul>
    </article>
  );
}

export default function App() {
  const data = sampleDashboardData;
  const summary = computeSummary(data.stocks);

  const sections = {
    top_candidates: data.stocks.filter((s) => s.board === 'top_candidates'),
    risk_blocked: data.stocks.filter((s) => s.board === 'risk_blocked'),
    needs_review: data.stocks.filter((s) => s.board === 'needs_review'),
    buy_zone: data.stocks.filter((s) => s.buy_zone_status.includes('buy zone'))
  };

  return (
    <main className="app-shell">
      <header>
        <h1>Model Factory Dashboard MVP v0.1</h1>
        <p className="muted">Generated: {new Date(data.generated_at).toLocaleString()}</p>
      </header>

      <section>
        <h2>Summary</h2>
        <div className="summary-grid">
          {SUMMARY_KEYS.map((item) => (
            <div className="summary-card" key={item.key}>
              <p className="summary-label">{item.label}</p>
              <p className="summary-value">{summary[item.key]}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="command-center">
        <h2>Command Center</h2>
        <p><span className="field">Mode:</span> {data.command_center.mode}</p>
        <p><span className="field">Data Source:</span> {data.command_center.data_source}</p>
        <p><span className="field">Benchmark:</span> {data.command_center.benchmark}</p>
        <p><span className="field">Note:</span> {data.command_center.note}</p>
      </section>

      <section>
        <h2>Top Candidates</h2>
        <div className="card-grid">{sections.top_candidates.map((s) => <StockCard stock={s} key={s.ticker} />)}</div>
      </section>

      <section>
        <h2>Risk-Blocked</h2>
        <div className="card-grid">{sections.risk_blocked.map((s) => <StockCard stock={s} key={s.ticker} />)}</div>
      </section>

      <section>
        <h2>Needs Review</h2>
        <div className="card-grid">{sections.needs_review.map((s) => <StockCard stock={s} key={s.ticker} />)}</div>
      </section>

      <section>
        <h2>Buy Zone Board</h2>
        <div className="card-grid">{sections.buy_zone.map((s) => <StockCard stock={s} key={`${s.ticker}-buy-zone`} />)}</div>
      </section>
    </main>
  );
}
