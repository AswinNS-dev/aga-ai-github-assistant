# Deployment Guide for AGA (AI GitHub Assistant)

This guide provides step-by-step instructions to deploy the AGA platform to production environments.

## Prerequisites
- A GitHub account.
- A Groq API Key (from console.groq.com).
- A GitHub Personal Access Token (PAT) with `repo` scopes.

---

## Option 1: Hugging Face Spaces (Recommended for Gradio)
Hugging Face provides native support for Gradio applications.

1. **Create a New Space**: Go to [huggingface.co/new-space](https://huggingface.co/new-space).
2. **Setup**:
   - **Space Name**: `aga-assistant`
   - **SDK**: `Docker` (Choose the Docker template).
3. **Environment Variables**:
   - In the Space settings, add the following variables:
     - `GITHUB_TOKEN`: Your PAT.
     - `GROQ_API_KEY`: Your Groq Key.
4. **Deploy**: Push your code to the Hugging Face Space repository.
   - *Note: Ensure your `Dockerfile` exposes port 7860.*

---

## Option 2: Azure Container Apps (Enterprise Ready)
For a professional, scalable deployment.

1. **Build & Push Docker Image**:
   ```bash
   docker build -t aga-platform .
   ```
2. **Deploy to Azure**:
   - Use the **Azure Container Apps** service.
   - Map Container Port `7860` to Ingress Port `443` (External).
3. **Secrets Management**:
   - Store `GITHUB_TOKEN` and `GROQ_API_KEY` in Azure Key Vault or as Container App Secrets.

---

## Option 3: Local Deployment (Production Mode)
If running on a private server:

1. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Set Environment Variables**:
   Create a `.env` file based on `.env.example`.
3. **Start the Server**:
   ```bash
   python app/main.py
   ```

---

## Technical Specifications
- **Runtime**: Python 3.11+
- **Port**: 7860
- **Variables Required**: `GITHUB_TOKEN`, `GROQ_API_KEY`
