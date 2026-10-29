import html
import logging
import re
from typing import List, Optional, Union
from github import Github, Repository, AuthenticatedUser
from github.GithubException import GithubException

logger = logging.getLogger(__name__)


def _sanitize_path(path: str) -> str:
    """Sanitize repository relative path preventing directory traversal."""
    if not path:
        return ""
    parts = [p for p in str(path).replace("\\", "/").split("/") if p and p != ".."]
    return "/".join(parts)


def _clean_repo_name(repo_name: str) -> str:
    """Extract and clean 'owner/repo' from URLs or raw identifiers."""
    cleaned = repo_name.strip()
    if re.match(r"^https?://", cleaned, flags=re.IGNORECASE):
        if not re.match(r"^https?://(www\.)?github\.com/", cleaned, flags=re.IGNORECASE):
            return repo_name.strip()
        cleaned = re.sub(r"^https?://(www\.)?github\.com/", "", cleaned, flags=re.IGNORECASE)

    if cleaned.startswith("git@github.com:"):
        cleaned = cleaned.replace("git@github.com:", "")
    cleaned = re.sub(r"^github\.com/", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\.git$", "", cleaned, flags=re.IGNORECASE)
    parts = [p for p in cleaned.strip("/").split("/") if p]
    if len(parts) >= 2 and not parts[0].startswith("http"):
        return f"{parts[0]}/{parts[1]}"
    if len(parts) == 1:
        return parts[0]
    return repo_name.strip()


class GitHubClient:
    """
    Professional wrapper for GitHub API operations.
    Handles repository management, content retrieval, file deployment, and deletion.
    """

    def __init__(self, token: str):
        if not token or not str(token).strip():
            raise ValueError("GitHub token must be provided and cannot be empty.")
        self.token = str(token).strip()
        self.client = Github(self.token)
        try:
            self.user: AuthenticatedUser = self.client.get_user()
            logger.info("GitHub client initialized.")
        except Exception as e:
            logger.error(f"GitHub Authentication failed: {e}")
            raise

    def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = True,
        auto_init: bool = True,
    ) -> Repository.Repository:
        """Create a new repository for the authenticated user."""
        if not name or not str(name).strip():
            raise ValueError("Repository name cannot be empty.")
        clean_name = str(name).strip()
        try:
            repo = self.user.create_repo(
                name=clean_name,
                description=description or "",
                private=private,
                auto_init=auto_init,
            )
            return repo
        except GithubException as e:
            logger.error(f"Failed to create repository {clean_name}: {e}")
            raise

    def list_repositories(self) -> List[Repository.Repository]:
        """List all repositories for the authenticated user."""
        try:
            return list(self.user.get_repos())
        except GithubException as e:
            logger.error(f"Failed to list repositories: {e}")
            raise

    def get_repo_details(self, repo_name: str) -> Repository.Repository:
        """Get details for a specific repository (e.g. 'username/repo' or GitHub URL)."""
        clean_name = _clean_repo_name(repo_name)
        try:
            return self.client.get_repo(clean_name)
        except GithubException as e:
            logger.error(f"Repository {clean_name} not found: {e}")
            raise

    def get_contents(self, repo_name: str, path: str = "") -> List:
        """Fetch contents of a repository at a specific path."""
        safe_path = _sanitize_path(path)
        clean_name = _clean_repo_name(repo_name)
        try:
            repo = self.client.get_repo(clean_name)
            contents = repo.get_contents(safe_path)
            if not isinstance(contents, list):
                contents = [contents]
            return contents
        except GithubException as e:
            # Status 404 with empty repo message is standard for uninitialized repos
            if e.status == 404 and "empty" in str(e).lower():
                logger.info(f"Repository {clean_name} is empty.")
                return []
            logger.error(f"Error fetching contents for {clean_name} at '{safe_path}': {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching contents for {clean_name} at '{safe_path}': {e}")
            return []

    def push_file(
        self,
        repo_name: str,
        path: str,
        content: Union[str, bytes],
        commit_message: str,
        branch: Optional[str] = None,
    ) -> str:
        """
        Push a file to a specific path in a repository (create or update).
        If branch is not specified, uses the repository default branch (e.g. main/master).
        """
        safe_path = _sanitize_path(path)
        if not safe_path:
            return "Error: Target file path cannot be empty."

        clean_name = _clean_repo_name(repo_name)
        try:
            repo = self.client.get_repo(clean_name)
            target_branch = branch if branch and branch.strip() else (repo.default_branch or "main")

            # Check if target is existing file or directory
            try:
                contents = repo.get_contents(safe_path, ref=target_branch)
                if isinstance(contents, list):
                    return (
                        f"Error: '{html.escape(safe_path)}' is a directory. "
                        f"Please specify a filename (e.g. {html.escape(safe_path.rstrip('/'))}/myfile.txt)"
                    )
                repo.update_file(
                    safe_path,
                    commit_message,
                    content,
                    contents.sha,
                    branch=target_branch,
                )
                return f"Successfully Updated: {html.escape(safe_path)}"
            except GithubException as e:
                if e.status == 404:
                    repo.create_file(
                        safe_path,
                        commit_message,
                        content,
                        branch=target_branch,
                    )
                    return f"Successfully Created: {html.escape(safe_path)}"
                else:
                    return f"GitHub Error ({e.status}): {html.escape(e.data.get('message', str(e)))}"
        except Exception as e:
            logger.error(f"Push failed: {clean_name}/{safe_path}: {e}")
            return f"System Error: {html.escape(str(e))}"

    def delete_file(
        self,
        repo_name: str,
        path: str,
        commit_message: str = "Delete file",
        branch: Optional[str] = None,
    ) -> str:
        """
        Delete a file from a repository at a specific path.
        """
        safe_path = _sanitize_path(path)
        if not safe_path:
            return "Error: File path cannot be empty."

        clean_name = _clean_repo_name(repo_name)
        try:
            repo = self.client.get_repo(clean_name)
            target_branch = branch if branch and branch.strip() else (repo.default_branch or "main")
            contents = repo.get_contents(safe_path, ref=target_branch)
            if isinstance(contents, list):
                return f"Error: '{html.escape(safe_path)}' is a directory, not a file."
            repo.delete_file(safe_path, commit_message, contents.sha, branch=target_branch)
            return f"Successfully Deleted: {html.escape(safe_path)}"
        except GithubException as e:
            logger.error(f"Failed to delete file {clean_name}/{safe_path}: {e}")
            raise

    def delete_repository(self, full_name: str):
        """Delete a repository. Note: Requires 'delete_repo' scope on token."""
        clean_name = _clean_repo_name(full_name)
        try:
            repo = self.client.get_repo(clean_name)
            repo.delete()
            logger.info(f"Deleted repository {clean_name}")
        except GithubException as e:
            logger.error(f"Failed to delete repository {clean_name}: {e}")
            raise

