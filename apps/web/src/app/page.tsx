type HealthResponse = {
  status: "ok";
  service: string;
  environment: string;
  version: string;
};

type ApiConnection = {
  connected: boolean;
  heading: string;
  detail: string;
};

const metrics = [
  {
    label: "Open observations",
    value: "18",
    change: "3 high priority",
    tone: "warning",
  },
  {
    label: "Corrective actions",
    value: "12",
    change: "4 due this week",
    tone: "attention",
  },
  {
    label: "Completed inspections",
    value: "47",
    change: "92% on schedule",
    tone: "success",
  },
  {
    label: "Training compliance",
    value: "96%",
    change: "2 renewals needed",
    tone: "info",
  },
];

const actions = [
  {
    title: "Replace damaged extension cord",
    project: "Meitner Wind Phase II",
    owner: "Jordan Lee",
    due: "Today",
    priority: "High",
  },
  {
    title: "Install missing excavation barricade",
    project: "North Ridge Solar",
    owner: "Morgan Cruz",
    due: "Tomorrow",
    priority: "High",
  },
  {
    title: "Update weekly eyewash inspection",
    project: "Juniper BESS",
    owner: "Sam Patel",
    due: "Aug 7",
    priority: "Medium",
  },
];

async function getApiConnection(): Promise<ApiConnection> {
  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  try {
    const response = await fetch(`${apiUrl}/api/v1/health`, {
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Health endpoint returned ${response.status}`);
    }

    const health: HealthResponse = await response.json();

    return {
      connected: health.status === "ok",
      heading: "API connected",
      detail: `${health.service} · ${health.environment} · v${health.version}`,
    };
  } catch {
    return {
      connected: false,
      heading: "API unavailable",
      detail: "Start the FastAPI development server on port 8000.",
    };
  }
}

function getCurrentDate(): string {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
  }).format(new Date());
}

export default async function Home() {
  const apiConnection = await getApiConnection();
  const currentDate = getCurrentDate();

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">
            G
          </div>

          <div>
            <p className="brand-name">GridGuard</p>
            <p className="brand-subtitle">Safety OS</p>
          </div>
        </div>

        <nav className="navigation" aria-label="Primary navigation">
          <a className="nav-link nav-link-active" href="#dashboard">
            <span aria-hidden="true">◫</span>
            Dashboard
          </a>

          <a className="nav-link" href="#projects">
            <span aria-hidden="true">⌂</span>
            Projects
          </a>

          <a className="nav-link" href="#inspections">
            <span aria-hidden="true">✓</span>
            Inspections
          </a>

          <a className="nav-link" href="#actions">
            <span aria-hidden="true">⚑</span>
            Corrective actions
          </a>

          <a className="nav-link" href="#training">
            <span aria-hidden="true">◇</span>
            Training
          </a>

          <a className="nav-link" href="#reports">
            <span aria-hidden="true">▤</span>
            Reports
          </a>
        </nav>

        <div className="sidebar-card">
          <p className="eyebrow">Field access</p>
          <h2>Scan. Submit. Solve.</h2>
          <p>
            Project QR codes give crews quick access to inspections and
            safety forms.
          </p>
          <button type="button">Generate QR code</button>
        </div>

        <div className="profile">
          <div className="avatar" aria-hidden="true">
            DS
          </div>

          <div>
            <p className="profile-name">David Spaulding</p>
            <p className="profile-role">Safety manager</p>
          </div>
        </div>
      </aside>

      <section className="workspace" id="dashboard">
        <header className="topbar">
          <div>
            <p className="eyebrow">{currentDate}</p>
            <h1>Good afternoon, David.</h1>
          </div>

          <div className="topbar-actions">
            <button className="secondary-button" type="button">
              Export report
            </button>

            <button className="primary-button" type="button">
              + New observation
            </button>
          </div>
        </header>

        <section className="hero-card">
          <div>
            <p className="eyebrow hero-eyebrow">Organization overview</p>
            <h2>Keep every project safe, visible, and accountable.</h2>
            <p>
              Three active renewable-energy projects are currently reporting
              through GridGuard.
            </p>
          </div>

          <div className="hero-score">
            <span>Safety pulse</span>
            <strong>91</strong>
            <small>Healthy</small>
          </div>
        </section>

        <section className="metrics-grid" aria-label="Safety metrics">
          {metrics.map((metric) => (
            <article className="metric-card" key={metric.label}>
              <div className={`metric-icon metric-icon-${metric.tone}`}>
                <span aria-hidden="true">●</span>
              </div>

              <p>{metric.label}</p>
              <strong>{metric.value}</strong>
              <span>{metric.change}</span>
            </article>
          ))}
        </section>

        <div className="content-grid">
          <section className="panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Current workload</p>
                <h2>Corrective actions</h2>
              </div>

              <button className="text-button" type="button">
                View all →
              </button>
            </div>

            <div className="action-list">
              {actions.map((action) => (
                <article className="action-row" key={action.title}>
                  <div className="action-check" aria-hidden="true" />

                  <div className="action-description">
                    <h3>{action.title}</h3>
                    <p>{action.project}</p>
                  </div>

                  <div className="action-owner">
                    <span>Assigned to</span>
                    <strong>{action.owner}</strong>
                  </div>

                  <div className="action-due">
                    <span>Due</span>
                    <strong>{action.due}</strong>
                  </div>

                  <span
                    className={`priority priority-${action.priority.toLowerCase()}`}
                  >
                    {action.priority}
                  </span>
                </article>
              ))}
            </div>
          </section>

          <aside className="panel activity-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Risk distribution</p>
                <h2>Open findings</h2>
              </div>
            </div>

            <div className="risk-total">
              <div className="risk-ring">
                <span>18</span>
                <small>Total</small>
              </div>

              <div className="risk-legend">
                <p>
                  <span className="legend-dot legend-high" />
                  High
                  <strong>3</strong>
                </p>

                <p>
                  <span className="legend-dot legend-medium" />
                  Medium
                  <strong>6</strong>
                </p>

                <p>
                  <span className="legend-dot legend-low" />
                  Low
                  <strong>9</strong>
                </p>
              </div>
            </div>

            <div
              className={`connection-card ${
                apiConnection.connected ? "connected" : "disconnected"
              }`}
            >
              <span className="connection-indicator" />

              <div>
                <strong>{apiConnection.heading}</strong>
                <p>{apiConnection.detail}</p>
              </div>
            </div>
          </aside>
        </div>

        <footer className="prototype-footer">
          GridGuard prototype · Mock safety data · Live API status
        </footer>
      </section>
    </main>
  );
}