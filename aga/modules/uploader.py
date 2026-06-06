import os
import magic
from typing import List, Dict, Optional

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
        "Dockerfile": "Docker"
    }

    EXTENSION_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".go": "Go",
        ".rs": "Rust",
        ".rb": "Ruby",
        ".php": "PHP"
    }

    def scan_path(self, folder_path: str) -> Dict:
        """Analyze a local directory for project metadata."""
        stats = {
            "languages": set(),
            "frameworks": set(),
            "file_count": 0,
            "structure": []
        }

        for root, dirs, files in os.walk(folder_path):
            # Exclude common ignores
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv']]
            
            for file in files:
                stats["file_count"] += 1
                ext = os.path.splitext(file)[1]
                
                if ext in self.EXTENSION_MAP:
                    stats["languages"].add(self.EXTENSION_MAP[ext])
                
                if file in self.FRAMEWORKS:
                    stats["frameworks"].add(self.FRAMEWORKS[file])

        return {
            "languages": list(stats["languages"]),
            "frameworks": list(stats["frameworks"]),
            "file_count": stats["file_count"]
        }

    def detect_mime(self, file_path: str) -> str:
        """Use libmagic to detect true file type."""
        return magic.from_file(file_path, mime=True)
