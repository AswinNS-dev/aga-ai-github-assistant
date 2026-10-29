from typing import Optional
from aga.core.ai_engine import AIEngine


class ReadmeGenerator:
    """
    Feature 4: AI README Generator.
    Supports multiple presentation styles: professional, open_source,
    startup, hackathon, and minimal.
    """

    STYLES = {
        "professional": "Formal, comprehensive, suitable for enterprise tools.",
        "open_source": "Community-focused, includes contribution guidelines and badges.",
        "startup": "Aggressive, feature-heavy, focused on unique selling points.",
        "hackathon": "Quick, punchy, focused on the 'how it works' and demo video.",
        "minimal": "Clean, focused strictly on installation and usage.",
    }

    def __init__(self, ai_engine: AIEngine):
        self.ai = ai_engine

    def generate(self, project_summary: str, style: str = "professional") -> str:
        """
        Generate a Markdown README for the project in the specified style.
        """
        if not project_summary or not str(project_summary).strip():
            raise ValueError("Project summary cannot be empty.")

        clean_style = style.lower().strip() if style else "professional"
        if clean_style not in self.STYLES:
            clean_style = "professional"

        custom_instructions = self.STYLES[clean_style]
        prompt_data = (
            f"Project Summary: {project_summary.strip()}\n"
            f"Style Instructions: {custom_instructions}"
        )

        return self.ai.generate_readme(prompt_data, style=clean_style)
