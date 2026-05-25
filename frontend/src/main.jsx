import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { analyzeRepo, fetchHistory } from "./api";
import "./styles.css";

function StatCard({ label, value }) {
  return (
    <div className="stat-card">
      <span>{label}</span>
      <strong>{value ?? "N/A"}</strong>
    </div>
  );
}

function App() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/facebook/react");
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadHistory() {
    try {
      setHistory(await fetchHistory());
    } catch {
      setHistory([]);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const result = await analyzeRepo(repoUrl);
      setAnalysis(result);
      await loadHistory();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Prompt 2</p>
        <h1>GitHub Repo Analyzer</h1>
        <p className="intro">
          Paste a public GitHub repository URL to fetch metadata, contributor
          activity, recent commits, and a saved analysis history.
        </p>

        <form className="search-form" onSubmit={handleSubmit}>
          <input
            value={repoUrl}
            onChange={(event) => setRepoUrl(event.target.value)}
            placeholder="https://github.com/owner/repo"
            aria-label="GitHub repository URL"
          />
          <button disabled={loading}>{loading ? "Analyzing..." : "Analyze"}</button>
        </form>

        {error && <div className="error-box">{error}</div>}
      </section>

      {analysis && (
        <section className="dashboard">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Repository</p>
              <h2>{analysis.full_name}</h2>
            </div>
            <a href={analysis.repo_url} target="_blank" rel="noreferrer">
              Open on GitHub
            </a>
          </div>

          <p className="description">
            {analysis.description || "No description provided."}
          </p>

          <div className="stats-grid">
            <StatCard label="Stars" value={analysis.stars} />
            <StatCard label="Forks" value={analysis.forks} />
            <StatCard label="Open issues" value={analysis.open_issues} />
            <StatCard label="Language" value={analysis.language || "Unknown"} />
            <StatCard label="Default branch" value={analysis.default_branch} />
            <StatCard label="License" value={analysis.license_name || "None"} />
          </div>

          <div className="metrics-panel">
            <h3>Activity summary</h3>
            <div className="metric-row">
              <span>Recent commits fetched</span>
              <strong>{analysis.metrics.recent_commit_count}</strong>
            </div>
            <div className="metric-row">
              <span>Activity label</span>
              <strong>{analysis.metrics.activity_label}</strong>
            </div>
            <div className="metric-row">
              <span>Most active recent day</span>
              <strong>{analysis.metrics.most_active_recent_day || "N/A"}</strong>
            </div>
            <div className="metric-row">
              <span>Top contributor</span>
              <strong>{analysis.metrics.top_contributor?.login || "N/A"}</strong>
            </div>
          </div>

          <div className="two-column">
            <section className="panel">
              <h3>Contributors</h3>
              <div className="list">
                {analysis.contributors.map((person) => (
                  <a
                    className="contributor"
                    href={person.html_url}
                    target="_blank"
                    rel="noreferrer"
                    key={person.login}
                  >
                    {person.avatar_url && (
                      <img src={person.avatar_url} alt="" loading="lazy" />
                    )}
                    <span>{person.login}</span>
                    <strong>{person.contributions}</strong>
                  </a>
                ))}
              </div>
            </section>

            <section className="panel">
              <h3>Recent commits</h3>
              <div className="list commits">
                {analysis.recent_commits.map((commit) => (
                  <a
                    className="commit"
                    href={commit.html_url}
                    target="_blank"
                    rel="noreferrer"
                    key={commit.sha}
                  >
                    <strong>{commit.sha}</strong>
                    <span>{commit.message || "No commit message"}</span>
                    <small>
                      {commit.author} ·{" "}
                      {commit.date ? commit.date.slice(0, 10) : "unknown date"}
                    </small>
                  </a>
                ))}
              </div>
            </section>
          </div>
        </section>
      )}

      <section className="history">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Stored in Postgres</p>
            <h2>Recent analyses</h2>
          </div>
          <button className="secondary" onClick={loadHistory}>
            Refresh
          </button>
        </div>

        {history.length === 0 ? (
          <p className="empty">No analyzed repos yet.</p>
        ) : (
          <div className="history-list">
            {history.map((item) => (
              <button
                key={item.id}
                onClick={() => setRepoUrl(item.repo_url)}
                className="history-item"
              >
                <span>
                  <strong>{item.full_name}</strong>
                  <small>{new Date(item.created_at).toLocaleString()}</small>
                </span>
                <span className="history-stats">
                  ★ {item.stars} · Forks {item.forks}
                </span>
              </button>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
