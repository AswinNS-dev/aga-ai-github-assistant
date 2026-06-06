import html
import logging
from typing import List, Optional
from github import Github, Repository, AuthenticatedUser
from github.GithubException import GithubException


def _sanitize_path(path: str) -> str:
    parts = [p for p in path.replace("\\", "/").split("/") if p and p != ".."]
    return "/".join(parts)

logger = logging.getLogger(__name__)

class GitHubClient:
    """
    Professional wrapper for GitHub API operations.
    Handles Feature 1: Repository Management.
    """
    def __init__(self, token: str):
        self.client = Github(token)
        try:
            self.user: AuthenticatedUser = self.client.get_user()
            logger.info(f"Authenticated as {self.user.login}")
        except Exception as e:
            logger.error(f"GitHub Authentication failed: {e}")
            raise

    def create_repository(
        self, 
        name: str, 
        description: str = "", 
        private: bool = True,
        auto_init: bool = True
    ) -> Repository.Repository:
        """Create a new repository for the authenticated user."""
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=auto_init
            )
            return repo
        except GithubException as e:
            logger.error(f"Failed to create repository {name}: {e}")
            raise

    def list_repositories(self) -> List[Repository.Repository]:
        """List all repositories for the authenticated user."""
        return list(self.user.get_repos())

    def get_repo_details(self, repo_name: str) -> Repository.Repository:
        """Get details for a specific repository (e.g. 'username/repo')."""
        try:
            return self.client.get_repo(repo_name)
        except GithubException as e:
            logger.error(f"Repository {repo_name} not found: {e}")
            raise

    def get_contents(self, repo_name: str, path: str = "") -> List:
        """Fetch contents of a repository at a specific path."""
        safe_path = _sanitize_path(path)
        try:
            repo = self.client.get_repo(repo_name)
            contents = repo.get_contents(safe_path)
            if not isinstance(contents, list):
                contents = [contents]
            return contents
        except Exception as e:
            logger.error(f"Error fetching contents for {repo_name} at {safe_path}: {e}")
            return []

    def push_file(self, repo_name: str, path: str, content: str, commit_message: str, branch: str = "main"):
        """Push a file to a specific path in a repository (create or update)."""
        safe_path = _sanitize_path(path)
        try:
            repo = self.client.get_repo(repo_name)
            try:
                contents = repo.get_contents(safe_path, ref=branch)
                
                if isinstance(contents, list):
                    return f"Error: '{html.escape(safe_path)}' is a directory. Please specify a filename (e.g. {html.escape(safe_path.rstrip('/'))}/myfile.txt)"
                
                repo.update_file(safe_path, commit_message, content, contents.sha, branch=branch)
                return f"Successfully Updated: {html.escape(safe_path)}"
            except GithubException as e:
                if e.status == 404:
                    repo.create_file(safe_path, commit_message, content, branch=branch)
                    return f"Successfully Created: {html.escape(safe_path)}"
                else:
                    return f"GitHub Error ({e.status}): {html.escape(e.data.get('message', str(e)))}"
        except Exception as e:
            logger.error(f"Push failed: {repo_name}/{safe_path}: {e}")
            return f"System Error: {html.escape(str(e))}"

    def delete_repository(self, full_name: str):
        """Delete a repository. Note: Requires 'delete_repo' scope on token."""
        try:
            repo = self.client.get_repo(full_name)
            repo.delete()
            logger.info(f"Deleted repository {full_name}")
        except GithubException as e:
            logger.error(f"Failed to delete repository {full_name}: {e}")
            raise
