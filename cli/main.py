import gradio as gr
import click
import os
from dotenv import load_dotenv
from aga.core.github_client import GitHubClient
from aga.core.ai_engine import AIEngine
from aga.modules.analyzer import RepoAnalyzer

load_dotenv()

SKIP_DIRS  = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', '.DS_Store'}
SKIP_FILES = {'.env', '.pyc', '.DS_Store'}


def collect_files(base_path):
    """Recursively collect all files, skipping junk/secret files."""
    file_map  = {}
    base_path = os.path.abspath(base_path)

    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for file in files:
            if any(file.endswith(s) or file == s for s in SKIP_FILES):
                continue
            local_path = os.path.join(root, file)
            repo_path  = os.path.relpath(local_path, base_path).replace("\\", "/")
            file_map[repo_path] = local_path

    return file_map


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        with open(path, "rb") as f:
            return f.read()


def push_files(client, repo_name, file_map, commit_message, branch, repo_prefix=""):
    repo = client.client.get_repo(repo_name)
    pushed, failed = [], []

    for repo_path, local_path in file_map.items():
        # Prepend the target repo folder prefix if specified
        if repo_prefix:
            full_repo_path = f"{repo_prefix.strip('/')}/{repo_path}"
        else:
            full_repo_path = repo_path

        content = read_file(local_path)
        try:
            try:
                existing = repo.get_contents(full_repo_path, ref=branch)
                repo.update_file(full_repo_path, commit_message, content, existing.sha, branch=branch)
            except Exception:
                repo.create_file(full_repo_path, commit_message, content, branch=branch)
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

    token    = click.prompt("GitHub Token")
    groq_key = click.prompt("Groq API Key")
    mode     = click.prompt("Create new repo or push to existing?", type=click.Choice(["new", "existing"]), default="existing")

    client = GitHubClient(token)
    ai     = AIEngine(groq_key)

    if mode == "new":
        repo_name = click.prompt("New repo name (e.g. my-project)")
        desc      = click.prompt("Description", default="")
        private   = click.confirm("Private repo?", default=True)
        repo      = client.create_repository(repo_name, desc, private)
        full_name = repo.full_name
        click.echo(f"Created: {repo.html_url}")
    else:
        full_name = click.prompt("Repo name (username/repo)")

    branch    = click.prompt("Branch", default="main")
    push_type = click.prompt("Push single file or entire folder?", type=click.Choice(["file", "folder"]), default="folder")

    if push_type == "file":
        file_path = click.prompt("Local file path")
        file_map  = {os.path.basename(file_path): os.path.abspath(file_path)}
    else:
        folder_path = click.prompt("Local folder path (press Enter for current directory)", default=".")
        file_map    = collect_files(folder_path)
        click.echo(f"Found {len(file_map)} files to push...")

    repo_prefix = click.prompt(
        "Target folder in repo (press Enter to push to repo root)",
        default=""
    )
    if repo_prefix:
        click.echo(f"Files will be placed under: {repo_prefix.strip('/')}/")
    else:
        click.echo("Files will be placed at the repo root.")

    sample     = ", ".join(list(file_map.keys())[:10])
    commit_msg = ai.generate_commit_message(f"Files: {sample}")
    click.echo(f"\nAI Commit Message: {commit_msg}")

    if not click.confirm("Proceed with push?"):
        click.echo("Aborted.")
        return

    click.echo("\nPushing...")
    pushed, failed = push_files(client, full_name, file_map, commit_msg, branch, repo_prefix)
    click.echo(f"\nDone! {len(pushed)} pushed, {len(failed)} failed.")


@cli.command()
@click.argument('name')
@click.option('--description', default="Created via AGA CLI", help="Repo description")
@click.option('--public', is_flag=True, help="Make repository public")
def create_repo(name, description, public):
    """Create a new GitHub repository."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        click.echo("Error: GITHUB_TOKEN not found in .env")
        return
    client = GitHubClient(token)
    repo   = client.create_repository(name, description, private=not public)
    click.echo(f"Repository created: {repo.html_url}")


@cli.command()
@click.argument('url')
def analyze(url):
    """Deeply analyze a GitHub repository."""
    token    = os.getenv("GITHUB_TOKEN")
    groq_key = os.getenv("GROQ_API_KEY")
    if not token or not groq_key:
        click.echo("Error: GITHUB_TOKEN or GROQ_API_KEY not found in .env")
        return
    client   = GitHubClient(token)
    ai       = AIEngine(groq_key)
    analyzer = RepoAnalyzer(client, ai)
    click.echo(f"Analyzing {url}...")
    result = analyzer.analyze(url)
    click.echo("\n--- Health Scores ---")
    for category, score in result['scores'].items():
        click.echo(f"{category.capitalize()}: {score}/100")
    click.echo("\n--- AI Analysis Summary ---")
    click.echo(result['report'][:500] + "...")


@cli.command()
@click.option('--port', default=7860, help='Port to run the web UI on')
def launch(port):
    """Launch the AGA web UI."""
    from app.main import demo
    click.echo(f"Launching AGA at http://127.0.0.1:{port}")
    demo.launch(server_port=port, theme=gr.themes.Soft())


if __name__ == "__main__":
    cli()
