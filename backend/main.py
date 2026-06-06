from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aga.core.github_client import GitHubClient
from aga.core.ai_engine import AIEngine
from aga.modules.analyzer import RepoAnalyzer
from aga.modules.readme_gen import ReadmeGenerator

app = FastAPI(title="AGA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Models ---
class AuthRequest(BaseModel):
    github_token: str
    groq_key: str

class RepoContentsRequest(BaseModel):
    github_token: str
    repo_name: str
    path: str = ""

class PushRequest(BaseModel):
    github_token: str
    groq_key: str
    repo_name: str
    file_path: str
    content: str
    commit_message: Optional[str] = ""

class AnalyzeRequest(BaseModel):
    github_token: str
    groq_key: str
    repo_url: str
    model: str = "llama-3.3-70b-versatile"

class ReadmeRequest(BaseModel):
    groq_key: str
    context: str
    style: str = "professional"

class CreateRepoRequest(BaseModel):
    github_token: str
    name: str
    description: str = ""
    private: bool = True


class DeleteFileRequest(BaseModel):
    github_token: str
    repo_name: str
    file_path: str
    message: str = ""

class DeleteRepoRequest(BaseModel):
    github_token: str
    repo_name: str


# --- Routes ---
@app.post("/auth")
def authenticate(req: AuthRequest):
    try:
        gh = GitHubClient(req.github_token)
        AIEngine(req.groq_key)
        user = gh.user
        return {
            "username": user.login,
            "avatar": user.avatar_url,
            "name": user.name or user.login,
            "public_repos": user.public_repos,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@app.post("/repos")
def list_repos(req: AuthRequest):
    try:
        gh = GitHubClient(req.github_token)
        repos = gh.list_repositories()
        return [
            {
                "full_name": r.full_name,
                "private": r.private,
                "stars": r.stargazers_count,
                "updated_at": r.updated_at.strftime("%Y-%m-%d"),
                "description": r.description or "",
                "url": r.html_url,
            }
            for r in repos
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/repos/contents")
def get_contents(req: RepoContentsRequest):
    try:
        gh = GitHubClient(req.github_token)
        contents = gh.get_contents(req.repo_name, req.path)
        return [
            {
                "name": c.name,
                "path": c.path,
                "type": c.type,
                "size": c.size,
                "url": c.html_url,
            }
            for c in contents
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/push")
def push_file(req: PushRequest):
    try:
        gh = GitHubClient(req.github_token)
        ai = AIEngine(req.groq_key)
        commit_msg = req.commit_message or ai.generate_commit_message(f"File: {req.file_path}")
        result = gh.push_file(req.repo_name, req.file_path, req.content, commit_msg)
        return {"message": result, "commit_message": commit_msg}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze")
def analyze_repo(req: AnalyzeRequest):
    try:
        gh = GitHubClient(req.github_token)
        ai = AIEngine(req.groq_key, model=req.model)
        analyzer = RepoAnalyzer(gh, ai)
        result = analyzer.analyze(req.repo_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/readme")
def generate_readme(req: ReadmeRequest):
    try:
        ai = AIEngine(req.groq_key)
        gen = ReadmeGenerator(ai)
        return {"readme": gen.generate(req.context, req.style)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/delete-file")
def delete_file(req: DeleteFileRequest):
    try:
        gh = GitHubClient(req.github_token)
        repo = gh.client.get_repo(req.repo_name)
        contents = repo.get_contents(req.file_path)
        if isinstance(contents, list):
            # It's a folder — delete all files recursively
            def delete_folder(path):
                items = repo.get_contents(path)
                for item in items:
                    if item.type == 'dir':
                        delete_folder(item.path)
                    else:
                        repo.delete_file(item.path, req.message or f"Delete {item.path}", item.sha)
            delete_folder(req.file_path)
            return {"message": f"Deleted folder: {req.file_path}"}
        else:
            repo.delete_file(contents.path, req.message or f"Delete {req.file_path}", contents.sha)
            return {"message": f"Deleted file: {req.file_path}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/delete-repo")
def delete_repo(req: DeleteRepoRequest):
    try:
        gh = GitHubClient(req.github_token)
        gh.delete_repository(req.repo_name)
        return {"message": f"Deleted repository: {req.repo_name}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/create-repo")
def create_repo(req: CreateRepoRequest):
    try:
        gh = GitHubClient(req.github_token)
        repo = gh.create_repository(req.name, req.description, req.private)
        return {"url": repo.html_url, "full_name": repo.full_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
