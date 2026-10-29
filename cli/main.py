import os
import click
from dotenv import load_dotenv
from aga.core.github_client import GitHubClient
from aga.core.ai_engine import AIEngine
from aga.modules.analyzer import RepoAnalyzer

load_dotenv()

SKIP_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv", ".DS_Store", "build", "dist"}
SKIP_FILES = {".env", ".pyc", ".DS_Store"}


def collect_files(base_path: str):
    """Recursively collect all files, skipping junk/secret files."""
    file_map = {}
    base_path = os.path.abspath(base_path)

    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for file in files:
            if any(file.endswith(s) or file == s for s in SKIP_FILES):
                continue
            local_path = os.path.join(root, file)
            repo_path = os.path.relpath(local_path, base_path).replace("\\", "/")
            file_map[repo_path] = local_path

    return file_map


def read_file(path: str):
    """Read file content as text or fallback to binary bytes."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        with open(path, "rb") as f:
            return f.read()


def push_files(client: GitHubClient, repo_name: str, file_map: dict, commit_message: str, branch: str, repo_prefix: str = ""):
    repo = client.get_repo_details(repo_name)
    target_branch = branch if branch and branch.strip() else (repo.default_branch or "main")
    pushed, failed = [], []

    for repo_path, local_path in file_map.items():
        if repo_prefix and repo_prefix.strip("/"):
            full_repo_path = f"{repo_prefix.strip('/')}/{repo_path}"
        else:
            full_repo_path = repo_path

        content = read_file(local_path)
        try:
            try:
                existing = repo.get_contents(full_repo_path, ref=target_branch)
                repo.update_file(full_repo_path, commit_message, content, existing.sha, branch=target_branch)
            except Exception:
                repo.create_file(full_repo_path, commit_message, content, branch=target_branch)
            pushed.append(full_repo_path)
            click.echo(f"  + {full_repo_path}")
        except Exception as e:
            failed.append(full_repo_path)
            click.echo(f"  x {full_repo_path} - {str(e)}")

    return pushed, failed


@click.group()
def cli():
    """AGA - AI GitHub Assistant CLI Tool"""
    pass


@cli.command()
def push():
    """Push a file or folder to GitHub with an AI-generated commit message."""
    click.echo("=== AGA Push ===")

    token = os.getenv("GITHUB_TOKEN") or click.prompt("GitHub Token", hide_input=True)
    groq_key = os.getenv("GROQ_API_KEY") or click.prompt("Groq API Key", hide_input=True)
    mode = click.prompt("Create new repo or push to existing?", type=click.Choice(["new", "existing"]), default="existing")

    try:
        client = GitHubClient(token)
        ai = AIEngine(groq_key)
    except Exception as e:
        raise click.ClickException(f"Authentication failed: {e}")

    if mode == "new":
        repo_name = click.prompt("New repo name (e.g. my-project)")
        desc = click.prompt("Description", default="")
        private = click.confirm("Private repo?", default=True)
        try:
            repo = client.create_repository(repo_name, desc, private)
            full_name = repo.full_name
            click.echo(f"Created: {repo.html_url}")
        except Exception as e:
            raise click.ClickException(f"Failed to create repository: {e}")
    else:
        full_name = click.prompt("Repo name (username/repo)")

    branch = click.prompt("Branch (leave blank for default branch)", default="")
    push_type = click.prompt("Push single file or entire folder?", type=click.Choice(["file", "folder"]), default="folder")

    if push_type == "file":
        file_path = click.prompt("Local file path")
        if not os.path.exists(file_path):
            raise click.ClickException(f"Local file does not exist: {file_path}")
        file_map = {os.path.basename(file_path): os.path.abspath(file_path)}
    else:
        folder_path = click.prompt("Local folder path (press Enter for current directory)", default=".")
        if not os.path.isdir(folder_path):
            raise click.ClickException(f"Directory does not exist: {folder_path}")
        file_map = collect_files(folder_path)
        click.echo(f"Found {len(file_map)} files to push...")

    if not file_map:
        click.echo("No files found to push.")
        return

    repo_prefix = click.prompt(
        "Target folder in repo (press Enter to push to repo root)",
        default=""
    )
    if repo_prefix:
        click.echo(f"Files will be placed under: {repo_prefix.strip('/')}/")
    else:
        click.echo("Files will be placed at the repo root.")

    sample = ", ".join(list(file_map.keys())[:10])
    commit_msg = ai.generate_commit_message(f"Files: {sample}")
    click.echo(f"\nAI Commit Message: {commit_msg}")

    if not click.confirm("Proceed with push?"):
        click.echo("Aborted.")
        return

    click.echo("\nPushing...")
    pushed, failed = push_files(client, full_name, file_map, commit_msg, branch, repo_prefix)
    click.echo(f"\nDone! {len(pushed)} pushed, {len(failed)} failed.")
    if failed:
        raise click.ClickException(f"{len(failed)} files failed to push.")


@cli.command()
@click.argument("name")
@click.option("--description", default="Created via AGA CLI", help="Repo description")
@click.option("--public", is_flag=True, help="Make repository public")
def create_repo(name: str, description: str, public: bool):
    """Create a new GitHub repository."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise click.ClickException("GITHUB_TOKEN not found in environment or .env file.")
    try:
        client = GitHubClient(token)
        repo = client.create_repository(name, description, private=not public)
        click.echo(f"Repository created: {repo.html_url}")
    except Exception as e:
        raise click.ClickException(f"Failed to create repository: {e}")


@cli.command()
@click.argument("url")
def analyze(url: str):
    """Deeply analyze a GitHub repository."""
    token = os.getenv("GITHUB_TOKEN")
    groq_key = os.getenv("GROQ_API_KEY")
    if not token:
        raise click.ClickException("GITHUB_TOKEN not found in environment or .env file.")
    if not groq_key:
        raise click.ClickException("GROQ_API_KEY not found in environment or .env file.")
    try:
        client = GitHubClient(token)
        ai = AIEngine(groq_key)
        analyzer = RepoAnalyzer(client, ai)
        click.echo(f"Analyzing {url}...")
        result = analyzer.analyze(url)
        click.echo("\n--- Health Scores ---")
        for category, score in result["scores"].items():
            click.echo(f"{category.capitalize()}: {score}/100")
        click.echo("\n--- AI Analysis Summary ---")
        report_preview = result["report"][:500]
        click.echo(report_preview + ("..." if len(result["report"]) > 500 else ""))
    except Exception as e:
        raise click.ClickException(f"Analysis failed: {e}")


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the web UI on")
@click.option("--port", default=7860, type=int, help="Port to run the web UI on")
@click.option("--share", is_flag=True, default=False, help="Create a public shareable link")
def launch(host: str, port: int, share: bool):
    """Launch the AGA web UI."""
    import gradio as gr
    from app.main import demo

    click.echo(f"Launching AGA at http://{host}:{port}")
    demo.launch(server_name=host, server_port=port, share=share, theme=gr.themes.Soft())


if __name__ == "__main__":
    cli()
