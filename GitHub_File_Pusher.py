import os
import re
import gradio as gr
from github import Github
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
 
 
summary_prompt = PromptTemplate(
    input_variables=["filename", "content"],
    template="""Look at this file and give a short 2-3 sentence summary of what it does or contains.
 
File name: {filename}
Content:
{content}
 
Summary:"""
)
 
commit_prompt = PromptTemplate(
    input_variables=["file_summaries"],
    template="""Based on these file summaries, write a short and clear git commit message.
Just the commit message, nothing else. Keep it under 72 characters.
 
Files being committed:
{file_summaries}
 
Commit message:"""
)
 
 
def read_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "[Binary file — content not readable as text]"
 
 
def summarize_files(llm, files):
    parser = StrOutputParser()
    chain = summary_prompt | llm | parser
 
    summaries = {}
    for file in files:
        filename = os.path.basename(file.name)
        content  = read_file(file.name)
        trimmed  = content[:3000]
        summary  = chain.invoke({"filename": filename, "content": trimmed})
        summaries[filename] = summary.strip()
 
    return summaries
 
 
def generate_commit_message(llm, summaries):
    parser = StrOutputParser()
    chain  = commit_prompt | llm | parser
 
    file_summaries = "\n".join([f"- {name}: {summary}" for name, summary in summaries.items()])
    message = chain.invoke({"file_summaries": file_summaries})
    return message.strip()
 
 
def sanitize_path(path: str) -> str:
    # Remove path traversal sequences and normalize
    parts = [p for p in path.replace("\\", "/").split("/") if p and p != ".."]
    return "/".join(parts)
 
 
def push_to_github(github_token, repo_name, folder_path, files, commit_message):
    g    = Github(github_token)
    repo = g.get_repo(repo_name)
    pushed = []
    failed = []
 
    for file in files:
        filename = os.path.basename(file.name)
        content  = read_file(file.name)
        safe_folder = sanitize_path(folder_path)
        path     = f"{safe_folder}/{filename}" if safe_folder else filename
 
        try:
            try:
                existing = repo.get_contents(path)
                repo.update_file(
                    path=path,
                    message=commit_message,
                    content=content,
                    sha=existing.sha
                )
            except Exception:
                repo.create_file(
                    path=path,
                    message=commit_message,
                    content=content
                )
            pushed.append(path)
 
        except Exception as e:
            failed.append(f"{filename} — {str(e)}")
 
    return pushed, failed
 
 
def run(groq_key, github_token, repo_name, folder_path, files):
    if not groq_key.strip():
        return "", "", "", "Please enter your Groq API Key."
    if not github_token.strip():
        return "", "", "", "Please enter your GitHub Token."
    if not repo_name.strip():
        return "", "", "", "Please enter the repo name (e.g. username/repo)."
    if not files:
        return "", "", "", "Please upload at least one file."
 
    safe_groq_key = re.sub(r"[^\w\-]", "", groq_key.strip())
    os.environ["GROQ_API_KEY"] = safe_groq_key
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
 
    try:
        summaries = summarize_files(llm, files)
    except Exception as e:
        return "", "", "", f"Error summarizing files: {str(e)}"
 
    summary_text = "\n\n".join([f"{name}:\n{summary}" for name, summary in summaries.items()])
 
    try:
        commit_message = generate_commit_message(llm, summaries)
    except Exception as e:
        return summary_text, "", "", f"Error generating commit message: {str(e)}"
 
    try:
        pushed, failed = push_to_github(github_token.strip(), repo_name.strip(), folder_path.strip(), files, commit_message)
    except Exception as e:
        return summary_text, commit_message, "", f"GitHub push failed: {str(e)}"
 
    status = ""
    if pushed:
        status += "Successfully pushed:\n" + "\n".join([f"  • {f}" for f in pushed])
    if failed:
        status += "\n\nFailed:\n" + "\n".join([f"  • {f}" for f in failed])
 
    return summary_text, commit_message, status, "Done!"
 
 
with gr.Blocks(title="GitHub File Pusher") as app:
 
    gr.Markdown("## GitHub File Pusher")
 
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Required Info")
            groq_key     = gr.Textbox(label="Groq API Key",   placeholder="gsk_...")
            github_token = gr.Textbox(label="GitHub Token",   placeholder="ghp_...")
            repo_name    = gr.Textbox(label="Repo Name",       placeholder="username/repo-name")
            folder_path  = gr.Textbox(label="Folder Path",     placeholder="MainFolder/Subfolder (optional)")
 
            gr.Markdown("### Files")
            files        = gr.File(label="Drag & Drop Files Here", file_count="multiple")
 
            push_btn     = gr.Button(" Summarize & Push", variant="primary")
 
        with gr.Column(scale=2):
            gr.Markdown("### Results")
            summary_out  = gr.Textbox(label="File Summaries",  lines=10)
            commit_out   = gr.Textbox(label="Commit Message",   lines=2)
            push_status  = gr.Textbox(label="Push Status",      lines=5)
            status_msg   = gr.Textbox(label="Overall Status",   lines=1)
 
    push_btn.click(
        fn=run,
        inputs=[groq_key, github_token, repo_name, folder_path, files],
        outputs=[summary_out, commit_out, push_status, status_msg]
    )
 
app.launch(share=True)