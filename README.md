# GitHub Repo Analyzer

**AI Support Engineer Assignment - Prompt 2 Submission**

## Project Overview

GitHub Repo Analyzer is a web tool that takes a public GitHub repository URL and presents detailed insights using the GitHub API. Built with React, Flask, and PostgreSQL—fully Dockerized and ready to run.

This project demonstrates:

- End-to-end full-stack development
- Real API integration with error handling
- Data persistence and querying
- Clean architecture and code organization
- Docker containerization

## Core Requirements (All Implemented)

| Requirement                       | Status | Implementation                                                |
| --------------------------------- | ------ | ------------------------------------------------------------- |
| Input field for GitHub repo link  | Yes    | React form with URL validation                                |
| Fetch and display repo metadata   | Yes    | Stars, forks, language, license, branch via GitHub API        |
| Display contributor activity data | Yes    | Top 8 contributors with avatars and contribution counts       |
| Display commit activity data      | Yes    | 12 recent commits with messages, authors, dates               |
| Handle rate-limiting gracefully   | Yes    | Detects rate limits, shows reset time, supports GitHub tokens |
| Handle failed API calls           | Yes    | URL validation, 404 handling, network error messages          |
| Store for later access            | Yes    | PostgreSQL persistence with analysis history                  |
| Additional metrics                | Yes    | Activity labels, most active day, top contributor             |

## Architecture

```
Frontend (React 18 + Vite)     Backend (Flask 3.0.3)      Database (PostgreSQL 16)
─────────────────────────────  ──────────────────────────  ───────────────────────
- main.jsx (UI + state)        - app.py (routes)           - repo_analyses table
- api.js (HTTP calls)          - github_client.py (API)    - JSONB data storage
- styles.css (plain CSS)       - db.py (persistence)       - Indexed queries
Port: 5173                      Port: 5000                  Port: 5433
```

## Tech Stack

- Frontend: React 18, Vite, Plain CSS (no dependencies)
- Backend: Flask 3.0.3, CORS enabled
- Database: PostgreSQL 16, psycopg3 driver
- API: GitHub REST API v2022-11-28
- Container: Docker Compose (3 services with healthchecks)

## Prerequisites

- Docker and Docker Compose installed
- Git
- Optional: GitHub personal access token for higher API rate limits

## Setup and Run

1. Clone the repository:

```bash
git clone https://github.com/ABHISHEK-YELMAMDI/github-repo-analyzer.git
cd github-repo-analyzer
```

2. Create environment file:

```bash
cp .env.example .env
```

3. (Optional) Add GitHub token to .env for higher rate limits:

```bash
GITHUB_TOKEN=your_github_token_here
POSTGRES_PASSWORD=your_secure_password
```

4. Start with Docker:

```bash
docker compose up --build
```

Then open:

- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
- Database: localhost:5433 (user: postgres, password: from .env)

Postgres is exposed on port 5433 to avoid conflicts with local Postgres on 5432.

## Getting a GitHub Token

For unauthenticated requests, GitHub limits you to 60 API calls per hour. To get a token:

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic) with `public_repo` scope
3. Copy the token and add to `.env` file
4. Rate limit increases to 5000 requests per hour

## API

| Method | Path         | Purpose                         |
| ------ | ------------ | ------------------------------- |
| GET    | /api/health  | Basic backend health check      |
| POST   | /api/analyze | Analyze a GitHub repository URL |
| GET    | /api/history | Return recent stored analyses   |

Example request:

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/facebook/react"}'
```

## Code Flow

User Submits a Repo URL:

1. Frontend (main.jsx#L30-35) - User pastes GitHub URL in form, clicks "Analyze" → handleSubmit() calls analyzeRepo()

2. HTTP Request (api.js#L3-10) - POST to /api/analyze with repo_url

3. Backend Route (app.py#L25-40) - Validates URL not empty, calls analyze_repo(repo_url)

4. URL Parsing (github_client.py#L20-30) - Validates domain is github.com, extracts owner and repo name, throws GitHubApiError if invalid

5. GitHub API Calls (github_client.py#L68-77) - Makes 3 requests:
   - /repos/{owner}/{repo} → metadata (stars, forks, language, etc.)
   - /repos/{owner}/{repo}/contributors → top 8 contributors
   - /repos/{owner}/{repo}/commits → 12 recent commits

6. Rate Limit Handling (github_client.py#L51-53) - Checks X-RateLimit-Remaining header, if 0 returns 429 with reset time, supports GITHUB_TOKEN env var for higher limits

7. Data Transformation (github_client.py#L79-130) - Extracts and calculates:
   - Activity label (Quiet/Moderate/Active based on commit count)
   - Most active recent day
   - Top contributor

8. Database Storage (db.py#L60-80) - Inserts into repo_analyses table, JSONB columns store nested data, returns serialized analysis with timestamp

9. Frontend Display (main.jsx#L55-160) - Sets analysis state, component re-renders with repo metadata grid, contributors list with avatars, recent commits timeline, calls loadHistory() to refresh analysis list

10. History Display (main.jsx#L165-200) - Shows all past analyses, clickable to load previous repo, stored in PostgreSQL with timestamps

## Key Files

database/init.sql - Database schema with repo_analyses table, JSONB columns for complex data storage, indexed timestamps for fast history queries

backend/app.py - Flask entry point with 3 routes (health check, analyze, history), CORS enabled, proper error handling with HTTP status codes

backend/github_client.py - GitHub API integration core logic. Validates repo URLs, makes 3 parallel API calls, detects and reports rate limits, transforms raw API data into metrics
Error Handling:

- Invalid URL format → 400
- Private/missing repo → 404
- Rate limit → 429 (with reset time)

backend/db.py - PostgreSQL connection. Connection pooling with context manager, insert analysis with JSON serialization, query history with timestamp ordering, convert timestamps to ISO format

frontend/src/main.jsx - React UI component. Form submission and validation, state management with hooks, error boundaries, auto-refresh history

frontend/src/api.js - Frontend API client. POST analyzeRepo() with error handling, GET fetchHistory() with error handling

frontend/src/styles.css - Styling. Plain CSS (no dependencies), responsive layout, clean component design

docker-compose.yml - Container orchestration. 3 services with proper dependencies, healthchecks for postgres, environment variables for configuration, volume mounting for database initialization

## How Windsurf Accelerated Development

Windsurf was instrumental in rapid MVP development:

1. Architecture Generation - Generated complete full-stack structure
2. API Scaffolding - Created Flask routes and error handling
3. GitHub Integration - Implemented API calls with rate limit detection
4. React Component - Generated form and state management
5. Database Layer - Produced SQL schema and persistence functions
6. Docker Setup - Generated docker-compose with proper configuration
7. Code Refinement - Manual tweaks for error messages and metrics

Result: ~80% boilerplate generated by Windsurf, allowing focus on architecture and user experience.

## Video Submission Focus

This project is optimized for a 7-minute demo covering:

1. Functionality - Analyze repos, display data, show error handling
2. Code Walkthrough - Data flow from UI → API → Database
3. Windsurf Usage - How AI IDE accelerated development
4. Dockerization - Complete containerized deployment

## Design Decisions

- Single-page app - All features visible, easier to demo
- Plain CSS - No dependencies, fast to load
- JSONB storage - Efficient nested data, indexed queries
- Top 8 contributors - Balance detail vs. performance
- Activity metrics - Simple health indicator
- Rate limit detection - Real-world API handling

## Notes

- All features are explained and demonstrated in ~7 minutes
- Code is clean, readable, and well-commented
- Proper error handling for real-world scenarios
- Docker setup is production-ready
- No over-engineering—focused on core requirements and clarity
