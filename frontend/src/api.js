const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

export async function analyzeRepo(repoUrl) {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ repo_url: repoUrl }),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Could not analyze repository.");
  }

  return data.analysis;
}

export async function fetchHistory() {
  const response = await fetch(`${API_BASE_URL}/api/history`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Could not load history.");
  }

  return data.history;
}
