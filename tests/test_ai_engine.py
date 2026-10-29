import pytest
from unittest.mock import MagicMock, patch

from aga.core.ai_engine import AIEngine


class TestAIEngine:
    def test_init_validation(self):
        with pytest.raises(ValueError, match="Groq API key must be provided"):
            AIEngine("")
        with pytest.raises(ValueError, match="Groq API key must be provided"):
            AIEngine("   ")

    @patch("aga.core.ai_engine.ChatGroq")
    def test_init_default_and_custom_model(self, mock_chat_groq):
        import os
        with patch.dict("os.environ", {}, clear=False):
            os.environ.pop("GROQ_MODEL", None)
            engine_default = AIEngine("gsk_key123")
            assert engine_default.model == "llama-3.3-70b-versatile"

        with patch.dict("os.environ", {"GROQ_MODEL": "custom-env-model"}):
            engine_env = AIEngine("gsk_key123")
            assert engine_env.model == "custom-env-model"

        engine_custom = AIEngine("gsk_key123", model="mixtral-8x7b-32768")
        assert engine_custom.model == "mixtral-8x7b-32768"


    @patch("aga.core.ai_engine.ChatGroq")
    def test_generate_commit_message_empty_input(self, mock_chat_groq):
        engine = AIEngine("gsk_key")
        assert engine.generate_commit_message("") == "chore: update project files"
        assert engine.generate_commit_message("   ") == "chore: update project files"

    @patch("aga.core.ai_engine.ChatGroq")
    def test_generate_commit_message_chain(self, mock_chat_groq):
        engine = AIEngine("gsk_key")
        with patch("langchain_core.prompts.PromptTemplate.__or__") as mock_or:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "feat: add user authentication\nExtra notes"
            mock_or.return_value.__or__.return_value = mock_chain

            result = engine.generate_commit_message("Added auth flow", style="conventional")
            assert result == "feat: add user authentication"

    @patch("aga.core.ai_engine.ChatGroq")
    def test_generate_readme_chain(self, mock_chat_groq):
        engine = AIEngine("gsk_key")
        with patch("langchain_core.prompts.PromptTemplate.__or__") as mock_or:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "# Project Title\n\nGenerated README content"
            mock_or.return_value.__or__.return_value = mock_chain

            result = engine.generate_readme("Simple web app", style="startup")
            assert "# Project Title" in result

    @patch("aga.core.ai_engine.ChatGroq")
    def test_analyze_repository_chain(self, mock_chat_groq):
        engine = AIEngine("gsk_key")
        with patch("langchain_core.prompts.PromptTemplate.__or__") as mock_or:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = "Health Score: 90/100\nNo critical security vulnerabilities found."
            mock_or.return_value.__or__.return_value = mock_chain

            result = engine.analyze_repository("main.py, test.py")
            assert "Health Score: 90/100" in result

    @patch("aga.core.ai_engine.ChatGroq")
    def test_model_not_found_raises_helpful_runtime_error(self, mock_chat_groq):
        engine = AIEngine("gsk_key")
        with patch("langchain_core.prompts.PromptTemplate.__or__") as mock_or:
            mock_chain = MagicMock()
            mock_chain.invoke.side_effect = Exception("Error code: 404 - {'error': {'code': 'model_not_found'}}")
            mock_or.return_value.__or__.return_value = mock_chain

            with pytest.raises(RuntimeError, match="is not accessible on your account. Please set GROQ_MODEL"):
                engine.generate_commit_message("some files")

