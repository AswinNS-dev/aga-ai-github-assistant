import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("backend.main.AIEngine")
@patch("backend.main.GitHubClient")
def test_auth_endpoint(mock_gh_class, mock_ai_class):
    mock_gh = MagicMock()
    mock_user = MagicMock()
    mock_user.login = "octocat"
    mock_user.avatar_url = "https://avatar.url"
    mock_user.name = "The Octocat"
    mock_user.public_repos = 42
    mock_gh.user = mock_user
    mock_gh_class.return_value = mock_gh

    response = client.post("/auth", json={"github_token": "ghp_mock", "groq_key": "gsk_mock"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "octocat"
    assert data["public_repos"] == 42


@patch("backend.main.GitHubClient")
def test_list_repos_endpoint(mock_gh_class):
    mock_gh = MagicMock()
    mock_repo = MagicMock()
    mock_repo.full_name = "octocat/hello-world"
    mock_repo.private = False
    mock_repo.stargazers_count = 120
    from datetime import datetime
    mock_repo.updated_at = datetime(2026, 2, 1)
    mock_repo.description = "Hello World Repo"
    mock_repo.html_url = "https://github.com/octocat/hello-world"
    mock_gh.list_repositories.return_value = [mock_repo]
    mock_gh_class.return_value = mock_gh

    response = client.post("/repos", json={"github_token": "ghp_mock", "groq_key": "gsk_mock"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "octocat/hello-world"
    assert data[0]["stars"] == 120


@patch("backend.main.GitHubClient")
def test_get_contents_endpoint(mock_gh_class):
    mock_gh = MagicMock()
    mock_item = MagicMock()
    mock_item.name = "README.md"
    mock_item.path = "README.md"
    mock_item.type = "file"
    mock_item.size = 1024
    mock_item.html_url = "https://github.com/octocat/hello-world/blob/main/README.md"
    mock_gh.get_contents.return_value = [mock_item]
    mock_gh_class.return_value = mock_gh

    response = client.post("/repos/contents", json={"github_token": "ghp_mock", "repo_name": "octocat/hello-world", "path": ""})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "README.md"


@patch("backend.main.AIEngine")
@patch("backend.main.GitHubClient")
def test_push_endpoint(mock_gh_class, mock_ai_class):
    mock_gh = MagicMock()
    mock_gh.push_file.return_value = "Successfully Created: test.py"
    mock_gh_class.return_value = mock_gh

    response = client.post(
        "/push",
        json={
            "github_token": "ghp_mock",
            "groq_key": "gsk_mock",
            "repo_name": "octocat/hello-world",
            "file_path": "test.py",
            "content": "print('hello')",
            "commit_message": "feat: add test",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "Successfully Created" in data["message"]


@patch("backend.main.ReadmeGenerator")
@patch("backend.main.AIEngine")
def test_readme_endpoint(mock_ai_class, mock_gen_class):
    mock_gen = MagicMock()
    mock_gen.generate.return_value = "# Sample Readme"
    mock_gen_class.return_value = mock_gen

    response = client.post(
        "/readme",
        json={"groq_key": "gsk_mock", "context": "My App", "style": "startup"},
    )
    assert response.status_code == 200
    assert response.json()["readme"] == "# Sample Readme"


@patch("backend.main.GitHubClient")
def test_create_repo_endpoint(mock_gh_class):
    mock_gh = MagicMock()
    mock_repo = MagicMock()
    mock_repo.html_url = "https://github.com/octocat/new-app"
    mock_repo.full_name = "octocat/new-app"
    mock_gh.create_repository.return_value = mock_repo
    mock_gh_class.return_value = mock_gh

    response = client.post(
        "/create-repo",
        json={"github_token": "ghp_mock", "name": "new-app", "description": "desc", "private": True},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "octocat/new-app"


@patch("backend.main.RepoAnalyzer")
@patch("backend.main.AIEngine")
@patch("backend.main.GitHubClient")
def test_analyze_endpoint(mock_gh, mock_ai, mock_analyzer_class):
    mock_analyzer = MagicMock()
    mock_analyzer.analyze.return_value = {
        "name": "octocat/hello-world",
        "scores": {"health": 90, "security": 80, "maintainability": 85, "documentation": 95},
        "report": "All checks passed.",
    }
    mock_analyzer_class.return_value = mock_analyzer

    response = client.post(
        "/analyze",
        json={
            "github_token": "ghp_mock",
            "groq_key": "gsk_mock",
            "repo_url": "https://github.com/octocat/hello-world",
        },
    )
    assert response.status_code == 200
    assert response.json()["scores"]["health"] == 90


@patch("backend.main.GitHubClient")
def test_delete_file_endpoint(mock_gh_class):
    mock_gh = MagicMock()
    mock_repo = MagicMock()
    mock_content = MagicMock()
    mock_content.path = "obsolete.txt"
    mock_content.sha = "sha_abc"
    mock_repo.get_contents.return_value = mock_content
    mock_gh.client.get_repo.return_value = mock_repo
    mock_gh_class.return_value = mock_gh

    response = client.post(
        "/delete-file",
        json={
            "github_token": "ghp_mock",
            "repo_name": "octocat/hello-world",
            "file_path": "obsolete.txt",
        },
    )
    assert response.status_code == 200
    assert "Deleted file" in response.json()["message"]
    mock_repo.delete_file.assert_called_once()


@patch("backend.main.GitHubClient")
def test_delete_repo_endpoint(mock_gh_class):
    mock_gh = MagicMock()
    mock_gh_class.return_value = mock_gh

    response = client.post(
        "/delete-repo",
        json={"github_token": "ghp_mock", "repo_name": "octocat/hello-world"},
    )
    assert response.status_code == 200
    assert "Deleted repository" in response.json()["message"]
    mock_gh.delete_repository.assert_called_once_with("octocat/hello-world")

