import pytest
from unittest.mock import MagicMock

from aga.modules.readme_gen import ReadmeGenerator


class TestReadmeGenerator:
    def test_generate_empty_summary_raises_error(self):
        mock_ai = MagicMock()
        gen = ReadmeGenerator(mock_ai)
        with pytest.raises(ValueError, match="Project summary cannot be empty"):
            gen.generate("")
        with pytest.raises(ValueError, match="Project summary cannot be empty"):
            gen.generate("   ")

    def test_generate_known_styles(self):
        mock_ai = MagicMock()
        mock_ai.generate_readme.return_value = "# Generated README"
        gen = ReadmeGenerator(mock_ai)

        for style in ["professional", "open_source", "startup", "hackathon", "minimal"]:
            res = gen.generate("A Python web scraper", style=style)
            assert res == "# Generated README"
            mock_ai.generate_readme.assert_called()

    def test_generate_unknown_style_falls_back_to_professional(self):
        mock_ai = MagicMock()
        mock_ai.generate_readme.return_value = "# Generated README"
        gen = ReadmeGenerator(mock_ai)

        res = gen.generate("A tool", style="unsupported_style")
        assert res == "# Generated README"
        prompt_arg = mock_ai.generate_readme.call_args[0][0]
        assert "Style Instructions: Formal, comprehensive" in prompt_arg
