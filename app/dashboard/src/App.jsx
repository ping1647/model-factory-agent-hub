import { useEffect, useState } from 'react';
import { sampleDashboardData } from './sampleDashboardData';

const SUMMARY_KEYS = [
  { key: 'total', label: 'Total' },
  { key: 'pass', label: 'Pass' },
  { key: 'warning', label: 'Warning' },
  { key: 'fail', label: 'Fail' },
  { key: 'needs_audit', label: 'Needs Audit' },
  { key: 'risk_blocked', label: 'Risk-Blocked' }
];

const SUMMARY_KEY_ALIASES = {
  total: ['total', 'total_count'],
  pass: ['pass', 'pass_count'],
  warning: ['warning', 'warning_count'],
  fail: ['fail', 'fail_count'],
  needs_audit: ['needs_audit', 'needs_audit_count'],
  risk_blocked: ['risk_blocked', 'risk_blocked_count']
};

const statusClass = (value = '') => value.toLowerCase().replace(/\s+/g, '_').replace(/-/g, '_');

function getSummaryValue(summary, key) {
  const aliases = SUMMARY_KEY_ALIASES[key] || [key];
  for (const alias of aliases) {
    const value = summary?.[alias];
    if (typeof value === 'number') {
      return value;
    }
  }
  return 0;
}

function getTickerLabel(item) {
  if (typeof item === 'string') {
    return item;
  }
  if (item && typeof item === 'object' && typeof item.ticker === 'string') {
    return item.ticker;
  }
  return 'Unknown';
}

function renderBlockers(blockers) {
  if (!Array.isArray(blockers) || blockers.length === 0) {
    return 'None';
  }
  return blockers.join(', ');
}

function renderTickerList(list) {
  if (!Array.isArray(list) || list.length === 0) {
    return 'None';
  }
  return list.map(getTickerLabel).join(', ');
}

async function fetchDashboardData() {
  const paths = ['/model-factory-agent-hub/dashboard_data.json', '/dashboard_data.json'];
  for (const path of paths) {
    const response = await fetch(path);
    if (response.ok) {
      return await response.json();
    }
  }
  throw new Error('Unable to load dashboard_data.json from known paths');
}

function StockCard({ stock }) {
  return (
    <article className="stock-card">
      <h3>{stock.ticker}</h3>
      <ul>
        <li><span className="field">model_id</span><span>{stock.model_id}</span></li>
        <li><span className="field">pipeline_status</span><span className={`tag ${statusClass(stock.pipeline_status)}`}>{stock.pipeline_status}</span></li>
        <li><span className="field">decision</span><span className={`tag ${statusClass(stock.decision)}`}>{stock.decision}</span></li>
        <li><span className="field">risk_score</span><span>{stock.risk_score} / 10</span></li>
        <li><span className="field">position_class</span><span>{stock.position_class}</span></li>
        <li><span className="field">buy_zone_status</span><span>{stock.buy_zone_status}</span></li>
        <li><span className="field">valuation_status</span><span>{stock.valuation_status}</span></li>
        <li><span className="field">blockers</span><span>{renderBlockers(stock.blockers)}</span></li>
        <li><span className="field">next_action</span><span>{stock.next_action}</span></li>
      </ul>
    </article>
  );
}

export default function App() {
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const loadData = async () => {
      setIsLoading(true);
      try {
        const jsonData = await fetchDashboardData();
        if (!isMounted) return;
        setData(jsonData);
        setLoadError(null);
      } catch (error) {
        if (!isMounted) return;
        setData(sampleDashboardData);
        setLoadError(error.message);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadData();

    return () => {
      isMounted = false;
    };
  }, []);

  if (isLoading) {
    return (
      <main className="app-shell">
        <header>
          <h1>Model Factory Dashboard MVP v0.1</h1>
        </header>
        <p className="muted">Loading dashboard data…</p>
      </main>
    );
  }

  const totalProcessed = getSummaryValue(data.summary, 'total');
  const generatedLabel = data.generated_at
    ? `Generated: ${new Date(data.generated_at).toLocaleString()}`
    : 'Generated: latest dashboard_data.json';

  return (
    <main className="app-shell">
      <header>
        <h1>Model Factory Dashboard MVP v0.1</h1>
        <p className="muted">{generatedLabel}</p>
        {loadError && <p className="muted">Using fallback sample data: {loadError}</p>}
      </header>

      <section>
        <h2>Summary</h2>
        <div className="summary-grid">
          {SUMMARY_KEYS.map((item) => (
            <div className="summary-card" key={item.key}>
              <p className="summary-label">{item.label}</p>
              <p className="summary-value">{getSummaryValue(data.summary, item.key)}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="command-center">
        <h2>Command Center</h2>
        <p><span className="field">Mode:</span> {data.command_center?.mode}</p>
        <p><span className="field">Data Source:</span> {data.command_center?.data_source}</p>
        <p><span className="field">Benchmark:</span> {data.command_center?.benchmark}</p>
        <p><span className="field">Note:</span> {data.command_center?.note}</p>
        <p><span className="field">Processed Universe:</span> {totalProcessed}</p>
        <p><span className="field">Top Candidates:</span> {renderTickerList(data.command_center?.top_candidates)}</p>
        <p><span className="field">Blocked Names:</span> {renderTickerList(data.command_center?.blocked_names)}</p>
        <p><span className="field">Needs Review:</span> {renderTickerList(data.command_center?.needs_review)}</p>
      </section>

      <section>
        <h2>Buy Zone Board</h2>
        <div className="card-grid">{(data.buy_zone_board || []).map((s) => <StockCard stock={s} key={`${s.ticker}-buy-zone`} />)}</div>
      </section>

      <section>
        <h2>Risk-Blocked</h2>
        <div className="card-grid">{(data.risk_blocked || []).map((s) => <StockCard stock={s} key={`${s.ticker}-risk-blocked`} />)}</div>
      </section>

      <section>
        <h2>Needs Audit</h2>
        <div className="card-grid">{(data.needs_audit || []).map((s) => <StockCard stock={s} key={`${s.ticker}-needs-audit`} />)}</div>
      </section>

      <section>
        <h2>Failed</h2>
        <div className="card-grid">{(data.failed || []).map((s) => <StockCard stock={s} key={`${s.ticker}-failed`} />)}</div>
      </section>

      <section>
        <h2>Warnings</h2>
        <div className="card-grid">{(data.warnings || []).map((s) => <StockCard stock={s} key={`${s.ticker}-warning`} />)}</div>
      </section>
    </main>
  );
}
