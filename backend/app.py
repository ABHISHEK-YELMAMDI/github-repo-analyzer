from flask import Flask, jsonify, request
from flask_cors import CORS

from db import init_db, list_history, save_analysis
from github_client import GitHubApiError, analyze_repo


app = Flask(__name__)
CORS(app)
init_db()


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/history")
def history():
    return jsonify({"history": list_history()})


@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    repo_url = data.get("repo_url", "")

    if not repo_url:
        return jsonify({"error": "Repository URL is required."}), 400

    try:
        analysis = analyze_repo(repo_url)
        saved = save_analysis(analysis)
        return jsonify({"analysis": saved})
    except GitHubApiError as error:
        return jsonify({"error": str(error)}), error.status_code
    except Exception:
        app.logger.exception("Unexpected analyzer error")
        return jsonify({"error": "Unexpected server error while analyzing the repo."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
