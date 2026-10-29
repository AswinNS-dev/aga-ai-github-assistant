"""
AGA — AI GitHub Assistant
An AI-powered GitHub assistant that automates file deployment, repository analysis,
README generation, and commit messages.
"""

from aga.core.github_client import GitHubClient
from aga.core.ai_engine import AIEngine
from aga.modules.analyzer import RepoAnalyzer
from aga.modules.readme_gen import ReadmeGenerator
from aga.modules.uploader import ProjectScanner

__version__ = "1.3.5"

__all__ = [
    "GitHubClient",
    "AIEngine",
    "RepoAnalyzer",
    "ReadmeGenerator",
    "ProjectScanner",
    "__version__",
]
