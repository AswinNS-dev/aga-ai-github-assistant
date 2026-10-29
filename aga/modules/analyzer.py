import re
import logging
from typing import Dict
from aga.core.github_client import GitHubClient
from aga.core.ai_engine import AIEngine

logger = logging.getLogger(__name__)


def extract_repo_name(url_or_name: str) -> str:
    """
    Extract 'owner/repo' identifier from any GitHub URL or string.
    Supports formats like:
      - https://github.com/owner/repo
      - http://github.com/owner/repo.git
      - github.com/owner/repo/tree/main
      - git@github.com:owner/repo.git
      - owner/repo
    """
    if not url_or_name or not str(url_or_name).strip():
        raise ValueError("Repository identifier cannot be empty.")

    cleaned = str(url_or_name).strip()

    # Ensure http/https URLs are strictly GitHub URLs
    if re.match(r"^https?://", cleaned, flags=re.IGNORECASE):
        if not re.match(r"^https?://(www\.)?github\.com/", cleaned, flags=re.IGNORECASE):
            raise ValueError(
                f"Invalid GitHub repository identifier: '{url_or_name}'. "
                "URL must be a GitHub repository (e.g. https://github.com/owner/repo)."
            )
        cleaned = re.sub(r"^https?://(www\.)?github\.com/", "", cleaned, flags=re.IGNORECASE)

    if cleaned.startswith("git@github.com:"):
        cleaned = cleaned.replace("git@github.com:", "")

    cleaned = re.sub(r"^github\.com/", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\.git$", "", cleaned, flags=re.IGNORECASE)

    parts = [p for p in cleaned.strip("/").split("/") if p]
    if len(parts) >= 2 and not parts[0].startswith("http"):
        return f"{parts[0]}/{parts[1]}"

    raise ValueError(
        f"Invalid GitHub repository identifier: '{url_or_name}'. "
        "Expected format: 'owner/repo' or 'https://github.com/owner/repo'"
    )


class RepoAnalyzer:
    """
    Feature 5: Repository Analyzer.
    Gathers quantitative health and documentation metrics from GitHub
    and invokes AI for deep qualitative architectural analysis.
    """

    def __init__(self, github_client: GitHubClient, ai_engine: AIEngine):
        self.gh = github_client
        self.ai = ai_engine

    def analyze(self, repo_url: str) -> Dict:
        """Perform deep analysis on a repository."""
        repo_name = extract_repo_name(repo_url)
        repo = self.gh.get_repo_details(repo_name)

        # 1. Quantitative Metrics
        has_readme = False
        try:
            readme_obj = repo.get_readme()
            has_readme = bool(readme_obj)
        except Exception:
            has_readme = False

        has_license = False
        try:
            has_license = bool(getattr(repo, "license", None))
        except Exception:
            has_license = False

        last_updated = repo.updated_at.strftime("%Y-%m-%d") if repo.updated_at else "Unknown"

        metrics = {
            "stars": int(repo.stargazers_count or 0),
            "forks": int(repo.forks_count or 0),
            "open_issues": int(repo.open_issues_count or 0),
            "has_readme": has_readme,
            "has_license": has_license,
            "last_updated": last_updated,
        }

        # 2. Qualitative AI Analysis
        structure_list = []
        try:
            contents = repo.get_contents("")
            if not isinstance(contents, list):
                contents = [contents]
            structure_list = [c.path for c in contents if hasattr(c, "path")]
        except Exception as e:
            logger.warning(f"Could not list root directory of {repo_name}: {e}")

        structure_str = "\n".join(structure_list) if structure_list else "(Empty or uninitialized repository)"
        ai_prompt_data = (
            f"Repo: {repo_name}\n"
            f"Files:\n{structure_str}\n"
            f"Metrics: {metrics}"
        )
        ai_report = self.ai.analyze_repository(ai_prompt_data)

        # 3. Final Scoring Logic
        # Health: based on baseline repository hygiene (README and License presence)
        if metrics["has_readme"] and metrics["has_license"]:
            health_score = 85
        elif metrics["has_readme"] or metrics["has_license"]:
            health_score = 65
        else:
            health_score = 40

        # Maintainability: based on open issues backlog
        if metrics["open_issues"] < 10:
            maintainability_score = 85
        elif metrics["open_issues"] < 50:
            maintainability_score = 70
        else:
            maintainability_score = 55

        # Documentation score
        documentation_score = 95 if metrics["has_readme"] else 20

        scores = {
            "health": health_score,
            "security": 75,  # Baseline security hygiene score
            "maintainability": maintainability_score,
            "documentation": documentation_score,
        }

        return {
            "name": repo_name,
            "metrics": metrics,
            "scores": scores,
            "report": ai_report,
        }
