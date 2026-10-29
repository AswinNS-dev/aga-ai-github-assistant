import os
import pytest
from aga.modules.uploader import ProjectScanner


class TestProjectScanner:
    def test_scan_path_not_found(self):
        scanner = ProjectScanner()
        with pytest.raises(FileNotFoundError):
            scanner.scan_path("non_existent_folder_xyz_123")

    def test_scan_path_not_a_directory(self, tmp_path):
        scanner = ProjectScanner()
        f = tmp_path / "single_file.txt"
        f.write_text("hello")
        with pytest.raises(NotADirectoryError):
            scanner.scan_path(str(f))

    def test_scan_path_detects_frameworks_and_languages(self, tmp_path):
        scanner = ProjectScanner()

        # Create files
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "requirements.txt").write_text("gradio\nclick")
        (tmp_path / "package.json").write_text('{"name": "test"}')
        (tmp_path / "app.ts").write_text("const x = 1;")

        # Create ignored folder
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "ignored.py").write_text("ignored")

        stats = scanner.scan_path(str(tmp_path))

        assert "Python" in stats["languages"]
        assert "TypeScript" in stats["languages"]
        assert "Python (Pip)" in stats["frameworks"]
        assert "JavaScript/TypeScript (Node.js)" in stats["frameworks"]
        # Ignored files should not be included
        assert stats["file_count"] == 4

    def test_detect_mime(self):
        scanner = ProjectScanner()
        assert scanner.detect_mime("test.html") == "text/html"
        assert scanner.detect_mime("test.json") == "application/json"
        assert scanner.detect_mime("test.unknown_ext_xyz") == "application/octet-stream"
