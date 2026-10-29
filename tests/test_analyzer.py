import pytest
from datetime import datetime
from unittest.mock import MagicMock

from aga.modules.analyzer import RepoAnalyzer, extract_repo_name


class TestExtractRepoName:
    def test_valid_urls(self):
        assert extract_repo_name("https://github.com/torvalds/linux") == "torvalds/linux"
        assert extract_repo_name("http://github.com/torvalds/linux.git") == "torvalds/linux"
        assert extract_repo_name("github.com/torvalds/linux") == "torvalds/linux"
        assert extract_repo_name("git@github.com:torvalds/linux.git") == "torvalds/linux"
        assert extract_repo_name("torvalds/linux") == "torvalds/linux"
        assert extract_repo_name("https://github.com/torvalds/linux/tree/main") == "torvalds/linux"

    def test_invalid_urls(self):
        with pytest.raises(ValueError, match="Repository identifier cannot be empty"):
            extract_repo_name("")
        with pytest.raises(ValueError, match="Invalid GitHub repository identifier"):
            extract_repo_name("https://google.com")
        with pytest.raises(ValueError, match="Invalid GitHub repository identifier"):
            extract_repo_name("justastring")


class TestRepoAnalyzer:
    def test_analyze_full_repo(self):
        mock_gh = MagicMock()
        mock_ai = MagicMock()
        mock_repo = MagicMock()

        mock_repo.stargazers_count = 100
        mock_repo.forks_count = 20
        mock_repo.open_issues_count = 5
        mock_repo.updated_at = datetime(2026, 1, 15)
        mock_repo.license = MagicMock()

        mock_file1 = MagicMock()
        mock_file1.path = "README.md"
        mock_file2 = MagicMock()
        mock_file2.path = "main.py"
        mock_repo.get_contents.return_value = [mock_file1, mock_file2]
        mock_repo.get_readme.return_value = mock_file1

        mock_gh.get_repo_details.return_value = mock_repo
        mock_ai.analyze_repository.return_value = "Detailed AI architectural report."

        analyzer = RepoAnalyzer(mock_gh, mock_ai)
        result = analyzer.analyze("https://github.com/owner/full-project")

        assert result["name"] == "owner/full-project"
        assert result["metrics"]["has_readme"] is True
        assert result["metrics"]["has_license"] is True
        assert result["metrics"]["stars"] == 100
        assert result["metrics"]["last_updated"] == "2026-01-15"
        assert result["scores"]["health"] == 85
        assert result["scores"]["maintainability"] == 85
        assert result["scores"]["documentation"] == 95
        assert "Detailed AI" in result["report"]

    def test_analyze_empty_or_minimal_repo(self):
        mock_gh = MagicMock()
        mock_ai = MagicMock()
        mock_repo = MagicMock()

        mock_repo.stargazers_count = 0
        mock_repo.forks_count = 0
        mock_repo.open_issues_count = 60
        mock_repo.updated_at = None
        mock_repo.license = None
        mock_repo.get_readme.side_effect = Exception("No README found")
        mock_repo.get_contents.side_effect = Exception("Empty repo")

        mock_gh.get_repo_details.return_value = mock_repo
        mock_ai.analyze_repository.return_value = "Empty repo report."

        analyzer = RepoAnalyzer(mock_gh, mock_ai)
        result = analyzer.analyze("owner/empty-repo")

        assert result["metrics"]["has_readme"] is False
        assert result["metrics"]["has_license"] is False
        assert result["metrics"]["last_updated"] == "Unknown"
        assert result["scores"]["health"] == 40
        assert result["scores"]["maintainability"] == 55
        assert result["scores"]["documentation"] == 20
