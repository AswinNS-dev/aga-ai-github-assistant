import os
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class AIEngine:
    """
    Core AI logic using Groq Llama 3.3.
    Handles commit message generation, README synthesis, and repository health audits.
    """

    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str, model: Optional[str] = None):
        if not api_key or not str(api_key).strip():
            raise ValueError("Groq API key must be provided and cannot be empty.")

        self.api_key = str(api_key).strip()
        self.model = model or os.getenv("GROQ_MODEL", self.DEFAULT_MODEL)

        self.llm = ChatGroq(
            groq_api_key=self.api_key,
            model_name=self.model,
            temperature=0.2,
        )
        self.parser = StrOutputParser()

    def _invoke(self, chain, params: dict) -> str:
        try:
            return chain.invoke(params)
        except Exception as e:
            err_msg = str(e).lower()
            if "model_not_found" in err_msg or "does not exist" in err_msg or "not have access" in err_msg:
                raise RuntimeError(
                    f"Groq model '{self.model}' is not accessible on your account. "
                    f"Please set GROQ_MODEL in your environment or .env file (e.g. GROQ_MODEL=openai/gpt-oss-120b or qwen/qwen3.8-27b)."
                ) from e
            raise

    def generate_commit_message(self, file_summaries: str, style: str = "conventional") -> str:
        """Generate a concise, standardized git commit message from file summaries."""
        clean_summaries = (file_summaries or "").strip()
        if not clean_summaries:
            return "chore: update project files"

        template = """You are an expert developer. Based on the following file summaries, 
write a {style} git commit message.

Summaries:
{file_summaries}

Commit message (one line, max 72 chars):"""

        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | self.parser
        raw_msg = self._invoke(chain, {"file_summaries": clean_summaries, "style": style or "conventional"})
        # Ensure single line and trimmed
        return raw_msg.strip().split("\n")[0].strip()

    def generate_readme(self, project_data: str, style: str = "professional") -> str:
        """Synthesize a complete README.md in the requested style."""
        clean_data = (project_data or "").strip()
        if not clean_data:
            clean_data = "Project documentation and setup instructions."

        template = """You are a documentation specialist. Create a {style} README.md for this project.
Include Title, Features, Tech Stack, and Installation.

Project context:
{project_data}

README.md content:"""

        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | self.parser
        return self._invoke(chain, {"project_data": clean_data, "style": style or "professional"})

    def analyze_repository(self, repo_content: str) -> str:
        """Perform deep architectural and security evaluation of project content."""
        clean_content = (repo_content or "").strip()
        if not clean_content:
            clean_content = "Empty repository structure."

        template = """Perform a deep architectural and security analysis of the following project.
Provide a Health Score (0-100) and specific improvement areas.

Project Content:
{repo_content}

Full Report:"""

        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | self.parser
        return self._invoke(chain, {"repo_content": clean_content})

