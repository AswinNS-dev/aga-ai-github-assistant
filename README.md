# AGA — AI GitHub Assistant

[![PyPI version](https://img.shields.io/pypi/v/aga-ai-github-assistant.svg)](https://pypi.org/project/aga-ai-github-assistant/)
[![Python Versions](https://img.shields.io/pypi/pyversions/aga-ai-github-assistant.svg)](https://pypi.org/project/aga-ai-github-assistant/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

An AI-powered GitHub automation assistant that automates file deployment, repository health audits, README synthesis, and commit message generation — available as a **Python library**, **CLI tool**, and interactive **Gradio web UI**.

---

## Features

- **AI File Deployment** — Upload local files and commit them directly to any repository branch with intelligent commit messages.
- **Repository Management** — Programmatically create, browse, list, and delete repositories with automatic branch resolution (`main`/`master`).
- **Deep Architectural & Health Analyzer** — Evaluate repository metrics (stars, forks, open issues, license, documentation) with Groq-powered AI architectural audits.
- **Multi-Style README Generator** — Synthesize tailored documentation (`professional`, `startup`, `open_source`, `hackathon`, `minimal`).
- **Dual Interfaces** — Run interactively in your browser with Gradio or from the terminal with the `aga` command.
- **Reusable Python Library** — Import core clients (`GitHubClient`, `AIEngine`, `RepoAnalyzer`, `ReadmeGenerator`, `ProjectScanner`) directly in your own applications.

---

## Tech Stack

- **AI Engine** — [Groq](https://groq.com) + [LangChain](https://langchain.com) (Llama 3.3 70B)
- **GitHub API** — [PyGithub](https://pygithub.readthedocs.io)
- **Web UI** — [Gradio](https://gradio.app)
- **CLI** — [Click](https://click.palletsprojects.com)

---

## Installation

```bash
pip install aga-ai-github-assistant
```

Requirements: **Python 3.9+**

---

## Configuration

Set your API credentials in your environment or in a `.env` file in your working directory (see [.env.example](.env.example)):

```env
GITHUB_TOKEN=ghp_your_personal_access_token_here
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional: AI Model Configuration (Default: llama-3.3-70b-versatile)
# Supported models depend on your Groq Cloud tier. Common alternatives include:
# - openai/gpt-oss-120b
# - qwen/qwen3.8-27b
# - llama-3.1-8b-instant
GROQ_MODEL=llama-3.3-70b-versatile

# Optional: Server & UI Configuration
PORT=7860
HOST=0.0.0.0
GRADIO_SHARE=False
```


---

## Quick Start

### 1. Web Application

Launch the interactive web UI using either the CLI entrypoint or the module runner:

```bash
# Using the CLI
aga launch --port 7860

# Or using the Python module
py -m app.main
```

Open your browser at `http://127.0.0.1:7860`.

---

### 2. Command Line Interface (CLI)

```bash
# Create a new repository
aga create-repo my-new-project --description "Built with AGA" --public

# Analyze a repository (URL, owner/repo, or git link)
aga analyze https://github.com/torvalds/linux

# Interactively push files or folders with AI commit messages
aga push
```

---

### 3. Python Library API

You can import and use AGA's core components directly inside your own Python projects:

```python
from aga import GitHubClient, AIEngine, RepoAnalyzer, ReadmeGenerator, ProjectScanner

# 1. Initialize Clients
gh = GitHubClient("ghp_your_token")
ai = AIEngine("gsk_your_groq_key")

# 2. Push a file (automatically falls back to repository default branch)
status = gh.push_file(
    repo_name="owner/repo",
    path="src/index.py",
    content="print('Hello from AGA')",
    commit_message="feat: initialize project",
)
print(status)

# 3. Analyze a repository
analyzer = RepoAnalyzer(gh, ai)
analysis = analyzer.analyze("https://github.com/owner/repo")
print("Scores:", analysis["scores"])
print("AI Report:", analysis["report"])

# 4. Generate a README
readme_gen = ReadmeGenerator(ai)
markdown = readme_gen.generate(
    project_summary="FastAPI backend with a React dashboard for real-time analytics",
    style="startup",
)
print(markdown)

# 5. Scan a local directory for languages and frameworks
scanner = ProjectScanner()
stats = scanner.scan_path("./my-project")
print("Languages:", stats["languages"])
print("Frameworks:", stats["frameworks"])
```

---

## Public Python API Reference

| Class / Function | Module | Description |
| :--- | :--- | :--- |
| `GitHubClient(token)` | `aga.core.github_client` | Wrapper for GitHub REST operations (create, list, get contents, push, delete). |
| `AIEngine(api_key, model=None)` | `aga.core.ai_engine` | Groq Llama 3.3 LLM engine for commits, READMEs, and audits. |
| `RepoAnalyzer(github_client, ai_engine)` | `aga.modules.analyzer` | Combines quantitative repository metrics with AI architectural reports. |
| `ReadmeGenerator(ai_engine)` | `aga.modules.readme_gen` | Generates structured Markdown READMEs in 5 distinct styles. |
| `ProjectScanner()` | `aga.modules.uploader` | Recursively inspects folders for languages, frameworks, and file counts. |

---

## Release Notes & Changelog

### v1.3.5 (Maintenance & Quality Release)
- **Packaging Integrity**: Fixed build isolation and directory traversal that previously bundled extraneous files into distribution wheels.
- **Public API Exports**: Exported core classes directly from `aga` root namespace and defined `__version__`.
- **Fast CLI Startup**: Made Gradio imports lazy in CLI commands, reducing `aga --help` execution latency.
- **Robust URL Parsing**: `RepoAnalyzer` and `GitHubClient` now safely parse URLs with `.git`, subpaths (`/tree/main`), `http://`, and shorthand `owner/repo`.
- **Dynamic Branch Resolution**: `push_file` now automatically detects and targets the repository's `default_branch` (`main`, `master`, etc.) when no branch is explicitly passed.
- **Directory Traversal Protection**: Enhanced `_sanitize_path` to strip path escapes and leading slashes safely.
- **Safe Explorer Handling**: Protected Gradio UI against unhandled `DataFrame` errors and directory selection exceptions.
- **Automated Test Suite**: Added 67 comprehensive unit, integration, and CLI tests with 100% pass rate.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
