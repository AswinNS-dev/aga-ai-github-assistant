import os
import mimetypes
from typing import Dict, List, Set


class ProjectScanner:
    """
    Feature 2: Advanced Project Upload & Scanning.
    Detects project types, languages, and frameworks.
    """

    # Signature files for framework detection
    FRAMEWORKS = {
        "requirements.txt": "Python (Pip)",
        "package.json": "JavaScript/TypeScript (Node.js)",
        "pom.xml": "Java (Maven)",
        "build.gradle": "Java (Gradle)",
        "go.mod": "Go",
        "Cargo.toml": "Rust",
        "composer.json": "PHP",
        "Gemfile": "Ruby",
        "manage.py": "Django",
        "app.py": "Flask/FastAPI",
        "next.config.js": "Next.js",
        "tailwind.config.js": "Tailwind CSS",
        "docker-compose.yml": "Docker Compose",
        "Dockerfile": "Docker",
    }

    EXTENSION_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".jsx": "React (JavaScript)",
        ".tsx": "React (TypeScript)",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP",
        ".html": "HTML",
        ".css": "CSS",
    }

    def scan_path(self, folder_path: str) -> Dict:
        """Analyze a local directory for project metadata."""
        if not folder_path or not os.path.exists(folder_path):
            raise FileNotFoundError(f"Directory not found: {folder_path}")
        if not os.path.isdir(folder_path):
            raise NotADirectoryError(f"Target path is not a directory: {folder_path}")

        languages: Set[str] = set()
        frameworks: Set[str] = set()
        file_count = 0

        for root, dirs, files in os.walk(folder_path):
            # Exclude common ignores
            dirs[:] = [
                d
                for d in dirs
                if d not in {".git", "node_modules", "__pycache__", "venv", ".venv", ".tox", "dist", "build"}
            ]

            for file in files:
                file_count += 1
                ext = os.path.splitext(file)[1].lower()

                if ext in self.EXTENSION_MAP:
                    languages.add(self.EXTENSION_MAP[ext])

                if file in self.FRAMEWORKS:
                    frameworks.add(self.FRAMEWORKS[file])

        return {
            "languages": sorted(list(languages)),
            "frameworks": sorted(list(frameworks)),
            "file_count": file_count,
        }

    def detect_mime(self, file_path: str) -> str:
        """Detect file MIME type using built-in mimetypes."""
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"
