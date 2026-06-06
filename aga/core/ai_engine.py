import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class AIEngine:
    """
    Core AI logic using Groq Llama 3.3.
    Handles Features 3 (Commits), 4 (README), and 5 (Analysis).
    """
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model,
            temperature=0.2
        )
        self.parser = StrOutputParser()

    def generate_commit_message(self, file_summaries: str, style: str = "conventional") -> str:
        template = """You are an expert developer. Based on the following file summaries, 
        write a {style} git commit message.
        
        Summaries:
        {file_summaries}
        
        Commit message (one line, max 72 chars):"""
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | self.parser
        return chain.invoke({"file_summaries": file_summaries, "style": style}).strip()

    def generate_readme(self, project_data: str, style: str = "professional") -> str:
        template = """You are a documentation specialist. Create a {style} README.md for this project.
        Include Title, Features, Tech Stack, and Installation.
        
        Project context:
        {project_data}
        
        README.md content:"""
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | self.parser
        return chain.invoke({"project_data": project_data, "style": style})

    def analyze_repository(self, repo_content: str) -> str:
        template = """Perform a deep architectural and security analysis of the following project.
        Provide a Health Score (0-100) and specific improvement areas.
        
        Project Content:
        {repo_content}
        
        Full Report:"""
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | self.parser
        return chain.invoke({"repo_content": repo_content})
