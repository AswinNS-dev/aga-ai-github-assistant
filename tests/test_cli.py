import os
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from cli.main import cli, collect_files, read_file


class TestCLI:
    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "AGA - AI GitHub Assistant CLI Tool" in result.output
        assert "create-repo" in result.output
        assert "analyze" in result.output
        assert "push" in result.output
        assert "launch" in result.output

    def test_create_repo_missing_token_fails(self):
        runner = CliRunner()
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(cli, ["create-repo", "my-repo"])
            assert result.exit_code != 0
            assert "GITHUB_TOKEN not found" in result.output

    @patch("cli.main.GitHubClient")
    def test_create_repo_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_repo = MagicMock()
        mock_repo.html_url = "https://github.com/user/my-repo"
        mock_client.create_repository.return_value = mock_repo
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_mock"}):
            result = runner.invoke(cli, ["create-repo", "my-repo", "--description", "Desc", "--public"])
            assert result.exit_code == 0
            assert "Repository created: https://github.com/user/my-repo" in result.output
            mock_client.create_repository.assert_called_once_with("my-repo", "Desc", private=False)

    def test_analyze_missing_credentials_fails(self):
        runner = CliRunner()
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(cli, ["analyze", "https://github.com/owner/repo"])
            assert result.exit_code != 0
            assert "GITHUB_TOKEN or GROQ_API_KEY" in result.output or "GITHUB_TOKEN not found" in result.output

    @patch("cli.main.RepoAnalyzer")
    @patch("cli.main.AIEngine")
    @patch("cli.main.GitHubClient")
    def test_analyze_success(self, mock_gh, mock_ai, mock_analyzer_class):
        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = {
            "scores": {"health": 85, "security": 75, "maintainability": 80, "documentation": 95},
            "report": "Overall great architecture.",
        }
        mock_analyzer_class.return_value = mock_analyzer

        runner = CliRunner()
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_mock", "GROQ_API_KEY": "gsk_mock"}):
            result = runner.invoke(cli, ["analyze", "owner/repo"])
            assert result.exit_code == 0
            assert "Health: 85/100" in result.output
            assert "Overall great architecture" in result.output

    def test_collect_files_and_read(self, tmp_path):
        sub = tmp_path / "src"
        sub.mkdir()
        f1 = sub / "app.py"
        f1.write_text("print('test')")

        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "secret.txt").write_text("ignored")

        file_map = collect_files(str(tmp_path))
        assert "src/app.py" in file_map
        assert ".git/secret.txt" not in file_map

        content = read_file(str(f1))
        assert content == "print('test')"

    def test_push_files(self, tmp_path):
        from cli.main import push_files
        mock_client = MagicMock()
        mock_repo = MagicMock()
        mock_repo.default_branch = "main"
        mock_client.get_repo_details.return_value = mock_repo
        # Simulate 404 so create_file is called
        mock_repo.get_contents.side_effect = Exception("Not found")

        f = tmp_path / "hello.py"
        f.write_text("print('hello')")
        file_map = {"hello.py": str(f)}

        pushed, failed = push_files(mock_client, "owner/repo", file_map, "feat: init", "main", repo_prefix="src")
        assert len(pushed) == 1
        assert pushed[0] == "src/hello.py"
        assert len(failed) == 0
        mock_repo.create_file.assert_called_once()
