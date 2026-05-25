import os
import re
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

import requests


GITHUB_API_BASE = "https://api.github.com"


class GitHubApiError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


def parse_repo_url(repo_url):
    parsed = urlparse(repo_url.strip())
    path = parsed.path.strip("/")

    if parsed.netloc not in {"github.com", "www.github.com"}:
        raise GitHubApiError("Please enter a public GitHub repository URL.")

    parts = path.split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise GitHubApiError("GitHub URL must look like https://github.com/owner/repo.")

    owner = parts[0]
    repo = re.sub(r"\.git$", "", parts[1])
    return owner, repo


def github_headers():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "csfirst-github-repo-analyzer",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def request_json(path, params=None):
    response = requests.get(
        f"{GITHUB_API_BASE}{path}",
        headers=github_headers(),
        params=params,
        timeout=12,
    )

    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        reset = response.headers.get("X-RateLimit-Reset")
        message = "GitHub API rate limit reached. Add a GITHUB_TOKEN or try again later."
        if reset:
            message += f" Reset time: {datetime.fromtimestamp(int(reset)).isoformat()}."
        raise GitHubApiError(message, 429)

    if response.status_code == 404:
        raise GitHubApiError("Repository not found or not public.", 404)

    if not response.ok:
        raise GitHubApiError("GitHub API request failed. Please try again.", response.status_code)

    return response.json()


def analyze_repo(repo_url):
    owner, repo = parse_repo_url(repo_url)

    repo_data = request_json(f"/repos/{owner}/{repo}")
    contributors = request_json(
        f"/repos/{owner}/{repo}/contributors",
        params={"per_page": 8, "anon": "false"},
    )
    commits = request_json(
        f"/repos/{owner}/{repo}/commits",
        params={"per_page": 12},
    )

    contributor_summary = [
        {
            "login": item.get("login") or "anonymous",
            "avatar_url": item.get("avatar_url"),
            "html_url": item.get("html_url"),
            "contributions": item.get("contributions", 0),
        }
        for item in contributors
    ]

    commit_summary = []
    commit_days = []
    for item in commits:
        commit = item.get("commit", {})
        author = commit.get("author") or {}
        date = author.get("date")
        if date:
            commit_days.append(date[:10])
        commit_summary.append(
            {
                "sha": item.get("sha", "")[:7],
                "message": (commit.get("message") or "").split("\n")[0],
                "author": author.get("name") or "unknown",
                "date": date,
                "html_url": item.get("html_url"),
            }
        )

    active_day = None
    if commit_days:
        active_day = Counter(commit_days).most_common(1)[0][0]

    recent_commit_count = len(commit_summary)
    activity_label = "Quiet"
    if recent_commit_count >= 10:
        activity_label = "Active"
    elif recent_commit_count >= 4:
        activity_label = "Moderate"

    top_contributor = contributor_summary[0] if contributor_summary else None

    return {
        "repo_url": repo_data.get("html_url", repo_url),
        "owner": owner,
        "repo": repo,
        "full_name": repo_data.get("full_name"),
        "description": repo_data.get("description"),
        "language": repo_data.get("language"),
        "stars": repo_data.get("stargazers_count", 0),
        "forks": repo_data.get("forks_count", 0),
        "open_issues": repo_data.get("open_issues_count", 0),
        "default_branch": repo_data.get("default_branch"),
        "license_name": (repo_data.get("license") or {}).get("name"),
        "contributors": contributor_summary,
        "recent_commits": commit_summary,
        "metrics": {
            "recent_commit_count": recent_commit_count,
            "top_contributor": top_contributor,
            "most_active_recent_day": active_day,
            "activity_label": activity_label,
        },
    }
