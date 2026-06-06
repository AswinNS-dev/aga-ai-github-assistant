from typing import Dict
from aga.core.github_client import GitHubClient
from aga.core.ai_engine import AIEngine

class RepoAnalyzer:
    """
    Feature 5: Repository Analyzer.
    Calculates health scores and provides reasoning.
    """
    def __init__(self, github_client: GitHubClient, ai_engine: AIEngine):
        self.gh = github_client
        self.ai = ai_engine

    def analyze(self, repo_url: str) -> Dict:
        """Performed deep analysis on a repository."""
        # Extracts 'owner/repo' from URL
        repo_name = repo_url.replace("https://github.com/", "").strip("/")
        repo = self.gh.get_repo_details(repo_name)
        
        # 1. Quantitative Metrics
        metrics = {
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "open_issues": repo.open_issues_count,
            "has_readme": bool(repo.get_contents("README.md") if self._check_file(repo, "README.md") else False),
            "has_license": bool(repo.license),
            "last_updated": repo.updated_at.strftime("%Y-%m-%d")
        }

        # 2. Qualitative AI Analysis
        # We fetch a summary of the root directory to feed the AI
        contents = repo.get_contents("")
        structure = "\n".join([c.path for c in contents])
        
        ai_report = self.ai.analyze_repository(f"Repo: {repo_name}\nFiles:\n{structure}\nMetrics: {metrics}")
        
        # 3. Final Scoring Logic (Mock logic for specific scores)
        scores = {
            "health": 85 if metrics["has_readme"] and metrics["has_license"] else 50,
            "security": 70, # Future: Scan for secrets or vulnerable dependencies
            "maintainability": 80 if metrics["open_issues"] < 10 else 60,
            "documentation": 95 if metrics["has_readme"] else 20
        }

        return {
            "name": repo_name,
            "metrics": metrics,
            "scores": scores,
            "report": ai_report
        }

    def _check_file(self, repo, path):
        try:
            repo.get_contents(path)
            return True
        except:
            return False
