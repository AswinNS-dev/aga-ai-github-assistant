from unittest.mock import MagicMock, patch
import pytest

from app.main import (
    authenticate,
    manage_repos,
    get_repo_folders,
    fetch_file_content,
    handle_push,
    run_analysis,
    generate_doc,
    handle_repo_creation,
    handle_explorer_click,
)


class TestAppHelpers:
    @patch("app.main.AIEngine")
    @patch("app.main.GitHubClient")
    def test_authenticate_success(self, mock_gh, mock_ai):
        msg, gh, ai = authenticate("token123", "groq123")
        assert "Successful" in msg
        assert gh is not None
        assert ai is not None

    def test_authenticate_failure(self):
        msg, gh, ai = authenticate("", "")
        assert "Error" in msg
        assert gh is None
        assert ai is None

    @patch("app.main.GitHubClient")
    def test_manage_repos(self, mock_gh_class):
        mock_gh = MagicMock()
        r = MagicMock()
        r.full_name = "user/repo"
        r.private = False
        r.stargazers_count = 10
        from datetime import datetime
        r.updated_at = datetime(2026, 1, 1)
        mock_gh.list_repositories.return_value = [r]
        mock_gh_class.return_value = mock_gh

        data, dropdown_update = manage_repos("token")
        assert len(data) == 1
        assert data[0][0] == "user/repo"

    @patch("app.main.GitHubClient")
    def test_get_repo_folders(self, mock_gh_class):
        mock_gh = MagicMock()
        item1 = MagicMock()
        item1.type = "dir"
        item1.path = "src"
        item2 = MagicMock()
        item2.type = "file"
        item2.path = "README.md"
        mock_gh.get_contents.return_value = [item1, item2]
        mock_gh_class.return_value = mock_gh

        table_data, path, dropdown = get_repo_folders("token", "user/repo", "")
        assert len(table_data) == 2
        assert "[DIR] src" in table_data[0][0]
        assert "[FILE] README.md" in table_data[1][0]

    @patch("app.main.GitHubClient")
    def test_fetch_file_content(self, mock_gh_class):
        mock_gh = MagicMock()
        mock_repo = MagicMock()
        mock_file = MagicMock()
        mock_file.name = "test.txt"
        mock_file.size = 2048
        mock_file.sha = "123456"
        mock_file.html_url = "https://github.com/..."
        mock_file.decoded_content = b"file content hello"
        mock_repo.get_contents.return_value = mock_file
        mock_gh.client.get_repo.return_value = mock_repo
        mock_gh_class.return_value = mock_gh

        content, details = fetch_file_content("token", "user/repo", "test.txt")
        assert content == "file content hello"
        assert "test.txt" in details

    @patch("app.main.GitHubClient")
    def test_handle_push_success(self, mock_gh_class):
        mock_gh = MagicMock()
        mock_gh.push_file.return_value = "Successfully Created: file.py"
        mock_gh_class.return_value = mock_gh

        res = handle_push("token", "", "user/repo", "file.py", "print(1)", "init")
        assert "Successfully Created" in res

    def test_handle_push_missing_fields(self):
        res = handle_push("token", "", "", "", "", "")
        assert "Warning: Missing required fields" in res

    @patch("app.main.RepoAnalyzer")
    @patch("app.main.AIEngine")
    @patch("app.main.GitHubClient")
    def test_run_analysis_success(self, mock_gh, mock_ai, mock_analyzer_class):
        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = {
            "scores": {"health": 85, "security": 70, "documentation": 90},
            "report": "Analysis summary",
        }
        mock_analyzer_class.return_value = mock_analyzer

        score_md, report = run_analysis("token", "groq", "https://github.com/u/r", "llama-3.3-70b-versatile")
        assert "Health Score: 85" in score_md
        assert report == "Analysis summary"

    def test_run_analysis_missing_credentials(self):
        score_md, report = run_analysis("", "", "url", "model")
        assert score_md == "Missing Credentials"

    @patch("app.main.ReadmeGenerator")
    @patch("app.main.AIEngine")
    def test_generate_doc(self, mock_ai, mock_gen_class):
        mock_gen = MagicMock()
        mock_gen.generate.return_value = "# README"
        mock_gen_class.return_value = mock_gen

        res = generate_doc("groq_key", "Summary", "startup")
        assert res == "# README"

    @patch("app.main.GitHubClient")
    def test_handle_repo_creation(self, mock_gh_class):
        mock_gh = MagicMock()
        mock_repo = MagicMock()
        mock_repo.full_name = "user/new-repo"
        mock_repo.html_url = "https://github.com/user/new-repo"
        mock_gh.create_repository.return_value = mock_repo
        mock_gh_class.return_value = mock_gh

        res = handle_repo_creation("token", "new-repo", "desc", True)
        assert "Successfully created" in res
        assert "user/new-repo" in res
