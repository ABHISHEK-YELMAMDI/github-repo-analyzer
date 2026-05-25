import json
import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/repo_analyzer",
)


@contextmanager
def get_connection():
    connection = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS repo_analyses (
              id SERIAL PRIMARY KEY,
              repo_url TEXT NOT NULL,
              owner TEXT NOT NULL,
              repo TEXT NOT NULL,
              full_name TEXT NOT NULL,
              description TEXT,
              language TEXT,
              stars INTEGER NOT NULL DEFAULT 0,
              forks INTEGER NOT NULL DEFAULT 0,
              open_issues INTEGER NOT NULL DEFAULT 0,
              default_branch TEXT,
              license_name TEXT,
              contributors JSONB NOT NULL DEFAULT '[]'::jsonb,
              recent_commits JSONB NOT NULL DEFAULT '[]'::jsonb,
              metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


def save_analysis(analysis):
    with get_connection() as connection:
        row = connection.execute(
            """
            INSERT INTO repo_analyses (
              repo_url, owner, repo, full_name, description, language,
              stars, forks, open_issues, default_branch, license_name,
              contributors, recent_commits, metrics
            )
            VALUES (
              %(repo_url)s, %(owner)s, %(repo)s, %(full_name)s,
              %(description)s, %(language)s, %(stars)s, %(forks)s,
              %(open_issues)s, %(default_branch)s, %(license_name)s,
              %(contributors)s::jsonb, %(recent_commits)s::jsonb,
              %(metrics)s::jsonb
            )
            RETURNING *
            """,
            {
                **analysis,
                "contributors": json.dumps(analysis["contributors"]),
                "recent_commits": json.dumps(analysis["recent_commits"]),
                "metrics": json.dumps(analysis["metrics"]),
            },
        ).fetchone()

    return serialize_row(row)


def list_history(limit=10):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, repo_url, full_name, stars, forks, language, created_at
            FROM repo_analyses
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()

    return [serialize_row(row) for row in rows]


def serialize_row(row):
    result = dict(row)
    if result.get("created_at"):
        result["created_at"] = result["created_at"].isoformat()
    return result
