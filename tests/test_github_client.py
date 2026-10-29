import pytest
from unittest.mock import MagicMock, patch
from github.GithubException import GithubException

from aga.core.github_client import GitHubClient, _sanitize_path, _clean_repo_name


class TestGitHubClientHelpers:
    def test_sanitize_path_traversal(self):
        assert _sanitize_path("../../etc/passwd") == "etc/passwd"
        assert _sanitize_path("foo/../bar") == "foo/bar"
        assert _sanitize_path("\\windows\\path\\file.txt") == "windows/path/file.txt"
        assert _sanitize_path("/leading/slash/") == "leading/slash"
        assert _sanitize_path("") == ""
        assert _sanitize_path(None) == ""

    def test_clean_repo_name(self):
        assert _clean_repo_name("https://github.com/owner/repo") == "owner/repo"
        assert _clean_repo_name("https://github.com/owner/repo.git") == "owner/repo"
        assert _clean_repo_name("http://github.com/owner/repo") == "owner/repo"
        assert _clean_repo_name("github.com/owner/repo") == "owner/repo"
        assert _clean_repo_name("git@github.com:owner/repo.git") == "owner/repo"
        assert _clean_repo_name("owner/repo") == "owner/repo"
        assert _clean_repo_name("https://github.com/owner/repo/tree/main") == "owner/repo"


class TestGitHubClient:
    def test_init_empty_token_raises_value_error(self):
        with pytest.raises(ValueError, match="GitHub token must be provided"):
            GitHubClient("")
        with pytest.raises(ValueError, match="GitHub token must be provided"):
            GitHubClient("   ")

    @patch("aga.core.github_client.Github")
    def test_init_success(self, mock_github_class):
        mock_instance = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "testuser"
        mock_instance.get_user.return_value = mock_user
        mock_github_class.return_value = mock_instance

        client = GitHubClient("ghp_test123")
        assert client.token == "ghp_test123"
        assert client.user.login == "testuser"
        mock_instance.get_user.assert_called_once()

    @patch("aga.core.github_client.Github")
    def test_create_repository_validation(self, mock_github_class):
        mock_instance = MagicMock()
        mock_github_class.return_value = mock_instance
        client = GitHubClient("token")

        with pytest.raises(ValueError, match="Repository name cannot be empty"):
            client.create_repository("")
        with pytest.raises(ValueError, match="Repository name cannot be empty"):
            client.create_repository("   ")

    @patch("aga.core.github_client.Github")
    def test_create_repository_success(self, mock_github_class):
        mock_instance = MagicMock()
        mock_user = MagicMock()
        mock_repo = MagicMock()
        mock_repo.full_name = "testuser/my-repo"
        mock_user.create_repo.return_value = mock_repo
        mock_instance.get_user.return_value = mock_user
        mock_github_class.return_value = mock_instance

        client = GitHubClient("token")
        result = client.create_repository("my-repo", description="Test repo", private=True)

        assert result.full_name == "testuser/my-repo"
        mock_user.create_repo.assert_called_once_with(
            name="my-repo", description="Test repo", private=True, auto_init=True
        )

    @patch("aga.core.github_client.Github")
    def test_list_repositories(self, mock_github_class):
        mock_instance = MagicMock()
        mock_user = MagicMock()
        repo1, repo2 = MagicMock(), MagicMock()
        mock_user.get_repos.return_value = [repo1, repo2]
        mock_instance.get_user.return_value = mock_user
        mock_github_class.return_value = mock_instance

        client = GitHubClient("token")
        repos = client.list_repositories()
        assert len(repos) == 2

    @patch("aga.core.github_client.Github")
    def test_get_repo_details(self, mock_github_class):
        mock_instance = MagicMock()
        mock_repo = MagicMock()
        mock_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_instance

        client = GitHubClient("token")
        repo = client.get_repo_details("https://github.com/owner/repo.git")
        mock_instance.get_repo.assert_called_with("owner/repo")
        assert repo == mock_repo

    @patch("aga.core.github_client.Github")
    def test_get_contents_empty_repo_returns_empty_list(self, mock_github_class):
        mock_instance = MagicMock()
        mock_repo = MagicMock()
        mock_repo.get_contents.side_effect = GithubException(404, {"message": "This repository is empty."}, None)
        mock_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_instance

        client = GitHubClient("token")
        contents = client.get_contents("owner/repo", "")
        assert contents == []

    @patch("aga.core.github_client.Github")
    def test_push_file_empty_path(self, mock_github_class):
        mock_instance = MagicMock()
        mock_github_class.return_value = mock_instance
        client = GitHubClient("token")
        res = client.push_file("owner/repo", "", "content", "commit")
        assert "cannot be empty" in res

    @patch("aga.core.github_client.Github")
    def test_push_file_creates_file_on_404(self, mock_github_class):
        mock_instance = MagicMock()
        mock_repo = MagicMock()
        mock_repo.default_branch = "master"
        # get_contents raises 404 (file does not exist)
        mock_repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"}, None)
        mock_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_instance

        client = GitHubClient("token")
        res = client.push_file("owner/repo", "test.py", "print('hello')", "init commit")
        assert "Successfully Created" in res
        mock_repo.create_file.assert_called_once_with(
            "test.py", "init commit", "print('hello')", branch="master"
        )

    @patch("aga.core.github_client.Github")
    def test_push_file_updates_existing_file(self, mock_github_class):
        mock_instance = MagicMock()
        mock_repo = MagicMock()
        mock_repo.default_branch = "main"
        mock_content_file = MagicMock()
        mock_content_file.sha = "sha123"
        mock_repo.get_contents.return_value = mock_content_file
        mock_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_instance

        client = GitHubClient("token")
        res = client.push_file("owner/repo", "test.py", "updated", "update commit", branch="dev")
        assert "Successfully Updated" in res
        mock_repo.update_file.assert_called_once_with(
            "test.py", "update commit", "updated", "sha123", branch="dev"
        )

    @patch("aga.core.github_client.Github")
    def test_push_file_directory_target_returns_error(self, mock_github_class):
        mock_instance = MagicMock()
        mock_repo = MagicMock()
        mock_repo.default_branch = "main"
        # returns list of contents representing a folder
        mock_repo.get_contents.return_value = [MagicMock(), MagicMock()]
        mock_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_instance

        client = GitHubClient("token")
        res = client.push_file("owner/repo", "src", "code", "msg")
        assert "is a directory" in res
        mock_repo.update_file.assert_not_called()
        mock_repo.create_file.assert_not_called()

    @patch("aga.core.github_client.Github")
    def test_delete_repository(self, mock_github_class):
        mock_instance = MagicMock()
        mock_repo = MagicMock()
        mock_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_instance

        client = GitHubClient("token")
        client.delete_repository("https://github.com/owner/repo.git")
        mock_instance.get_repo.assert_called_with("owner/repo")
        mock_repo.delete.assert_called_once()

    @patch("aga.core.github_client.Github")
    def test_delete_file_success(self, mock_github_class):
        mock_instance = MagicMock()
        mock_repo = MagicMock()
        mock_repo.default_branch = "main"
        mock_content = MagicMock()
        mock_content.sha = "sha_abc123"
        mock_repo.get_contents.return_value = mock_content
        mock_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_instance

        client = GitHubClient("token")
        res = client.delete_file("owner/repo", "test.py", "remove test", branch="main")
        assert "Successfully Deleted" in res
        mock_repo.delete_file.assert_called_once_with("test.py", "remove test", "sha_abc123", branch="main")

    @patch("aga.core.github_client.Github")
    def test_delete_file_directory_rejected(self, mock_github_class):
        mock_instance = MagicMock()
        mock_repo = MagicMock()
        mock_repo.default_branch = "main"
        mock_repo.get_contents.return_value = [MagicMock()]  # directory returns list
        mock_instance.get_repo.return_value = mock_repo
        mock_github_class.return_value = mock_instance

        client = GitHubClient("token")
        res = client.delete_file("owner/repo", "src")
        assert "is a directory, not a file" in res
        mock_repo.delete_file.assert_not_called()

    @patch("aga.core.github_client.Github")
    def test_delete_file_empty_path(self, mock_github_class):
        mock_github_class.return_value = MagicMock()
        client = GitHubClient("token")
        res = client.delete_file("owner/repo", "")
        assert "cannot be empty" in res

