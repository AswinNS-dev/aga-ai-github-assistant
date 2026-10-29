import aga
from aga import (
    GitHubClient,
    AIEngine,
    RepoAnalyzer,
    ReadmeGenerator,
    ProjectScanner,
    __version__,
)
from aga.core import GitHubClient as CoreGitHubClient
from aga.modules import RepoAnalyzer as ModuleRepoAnalyzer


def test_package_exports():
    assert __version__ == "1.3.5"
    assert GitHubClient is not None
    assert AIEngine is not None
    assert RepoAnalyzer is not None
    assert ReadmeGenerator is not None
    assert ProjectScanner is not None
    assert CoreGitHubClient is GitHubClient
    assert ModuleRepoAnalyzer is RepoAnalyzer


def test_cli_import():
    from cli.main import cli
    assert callable(cli)


def test_app_demo_import():
    from app.main import demo
    assert demo is not None
    assert hasattr(demo, "launch")
