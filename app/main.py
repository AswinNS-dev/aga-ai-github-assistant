import html
import gradio as gr
import os
from dotenv import load_dotenv

def sanitize_path(path: str) -> str:
    parts = [p for p in path.replace("\\", "/").split("/") if p and p != ".."]
    return "/".join(parts)

from aga.core.github_client import GitHubClient
from aga.core.ai_engine import AIEngine
from aga.modules.uploader import ProjectScanner
from aga.modules.analyzer import RepoAnalyzer
from aga.modules.readme_gen import ReadmeGenerator

load_dotenv()

# --- Backend Logic Helpers ---
def authenticate(token, groq_key):
    try:
        gh = GitHubClient(token)
        ai = AIEngine(groq_key)
        return "Authentication Successful!", gh, ai
    except Exception as e:
        return f"Error: {str(e)}", None, None

def manage_repos(token):
    try:
        gh = GitHubClient(token)
        repos = gh.list_repositories()
        names = [r.full_name for r in repos]
        # Added a specific format for the table
        data = [[r.full_name, "Private" if r.private else "Public", r.stargazers_count, r.updated_at.strftime("%Y-%m-%d")] for r in repos]
        return data, gr.update(choices=names)
    except Exception as e:
        return [["Error", str(e), "", ""]], gr.update(choices=[])

def get_repo_folders(token, repo_full_name, current_path=""):
    if not repo_full_name: 
        return [], current_path, gr.update(choices=[])
    try:
        gh = GitHubClient(token)
        contents = gh.get_contents(repo_full_name, current_path)
        
        table_data = []
        file_list = []
        if current_path:
            table_data.append([".. (Go Back)", "Parent Folder", "Enter"])
            
        for c in contents:
            item_type = "DIR" if c.type == "dir" else "FILE"
            table_data.append([f"[{item_type}] {c.path.split('/')[-1]}", "Folder" if c.type == "dir" else "File", "Set as Target"])
            if c.type == "file":
                file_list.append(c.path)
            
        return table_data, current_path, gr.update(choices=file_list)
    except Exception as e:
        print(f"Explorer Error: {e}")
        return [], current_path, gr.update(choices=[])

def fetch_file_content(token, repo_full_name, file_path):
    if not repo_full_name or not file_path:
        return "", "No file selected"
    try:
        gh = GitHubClient(token)
        repo = gh.client.get_repo(repo_full_name)
        content_file = repo.get_contents(file_path)
        decoded_content = content_file.decoded_content.decode("utf-8", errors="ignore")
        
        details = f"""
        **File Information:**
        - **Name:** {html.escape(content_file.name)}
        - **Size:** {content_file.size / 1024:.2f} KB
        - **SHA:** `{html.escape(content_file.sha)}`
        - [View on GitHub]({html.escape(content_file.html_url)})
        """
        return decoded_content, details
    except Exception as e:
        return f"Error fetching file: {str(e)}", f"Error: {str(e)}"

def navigate_explorer(token, repo_full_name, evt: gr.SelectData, current_path):
    # evt.index[0] is row, evt.index[1] is column
    row_idx = evt.index[0]
    col_idx = evt.index[1]
    
    # We need the data from the table to know what was clicked
    # Since we can't easily get the data here without passing it, 
    # we'll use a hack or just re-fetch for now? No, better to have the data passed.
    # Actually, navigate_explorer needs the table data.
    pass

def handle_explorer_click(token, repo_full_name, current_path, table_data, evt: gr.SelectData):
    # table_data can be a pandas DataFrame or a list
    if table_data is None or repo_full_name is None:
        return table_data, current_path, ""
    
    # Convert to list if it's a DataFrame
    import pandas as pd
    if isinstance(table_data, pd.DataFrame):
        data_list = table_data.values.tolist()
    else:
        data_list = table_data
        
    if not data_list:
        return table_data, current_path, ""
    
    row = data_list[evt.index[0]]
    item_name_with_type = str(row[0])
    item_type = str(row[1])
    
    clean_name = item_name_with_type.replace("[DIR] ", "").replace("[FILE] ", "").strip()
    
    # Logic for Navigation
    if item_name_with_type == ".. (Go Back)":
        new_path = "/".join(current_path.strip("/").split("/")[:-1])
        new_data, path_state, _ = get_repo_folders(token, repo_full_name, new_path)
        return new_data, path_state, new_path
        
    if item_type == "Folder" and evt.index[1] == 0: # Clicked folder name
        new_path = f"{current_path}/{clean_name}".strip("/")
        new_data, path_state, _ = get_repo_folders(token, repo_full_name, new_path)
        return new_data, path_state, new_path

    # Logic for Selecting Path
    if evt.index[1] == 2: # Clicked "Action" column
        selected_path = f"{current_path}/{clean_name}".strip("/")
        return table_data, current_path, selected_path

    return table_data, current_path, current_path

def handle_file_upload(files, current_path):
    if not files:
        return "", current_path
    
    # Store the content of the first file
    file_info = files[0]
    file_path = file_info.name
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}", current_path
        
    filename = os.path.basename(file_path)
    
    # Smart path logic:
    # If current_path is empty, just use filename
    # If current_path is a folder, append filename
    if not current_path:
        new_path = filename
    elif current_path.endswith(filename):
        new_path = current_path # Already has it
    else:
        # Check if it's likely a directory (doesn't have an extension or is a known folder)
        new_path = f"{current_path.rstrip('/')}/{filename}"
        
    return content, new_path

def handle_push(token, manual_repo, selected_repo, path, content, commit):
    target_repo = manual_repo if manual_repo else selected_repo
    if not target_repo or not path or not content:
        return "<div style='color: #ffa500; font-weight: bold;'>Warning: Missing required fields (Repo, Path, or Content)</div>"

    safe_path = sanitize_path(path)
    try:
        gh = GitHubClient(token)
        msg = commit if commit else f"Deployed via AGA Platform: {safe_path}"
        result = gh.push_file(target_repo, safe_path, content, msg)
        color = "#00ff00" if "Successfully" in result else "#ff4b4b"
        return f"<div style='color: {color}; font-weight: bold; border: 1px solid {color}; padding: 10px; border-radius: 5px;'>{html.escape(result)}</div>"
    except Exception as e:
        return f"<div style='color: #ff4b4b; font-weight: bold;'>Error: {html.escape(str(e))}</div>"

def update_repo_visibility(mode):
    if mode == "Select Existing":
        return gr.update(visible=True), gr.update(visible=False)
    return gr.update(visible=False), gr.update(visible=True)

def run_analysis(token, groq_key, url, model):
    if not token or not groq_key:
        return "Missing Credentials", "Please provide BOTH GitHub Token and Groq API Key in the Authentication tab."
    if not url:
        return "Missing URL", "Please enter a valid GitHub repository URL."
        
    try:
        gh = GitHubClient(token)
        ai = AIEngine(groq_key, model=model)
        analyzer = RepoAnalyzer(gh, ai)
        res = analyzer.analyze(url)
        
        score_md = f"### Health Score: {res['scores']['health']} | Security: {res['scores']['security']} | Docs: {res['scores']['documentation']}"
        return score_md, res['report']
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "invalid_api_key" in error_msg:
            return "Authentication Failed", "Your Groq API Key is invalid or expired. Please check the Authentication tab. \n\nGet a new key at: https://console.groq.com/"
        return f"Analysis Failed", error_msg

def generate_doc(groq_key, context, style):
    if not groq_key:
        return "Error: Groq API Key is missing. Please provide it in the Authentication tab."
        
    try:
        ai = AIEngine(groq_key)
        gen = ReadmeGenerator(ai)
        return gen.generate(context, style)
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "invalid_api_key" in error_msg:
            return "Invalid Groq Key. Please update it in the Authentication tab."
        return f"Error: {error_msg}"

def handle_repo_creation(token, name, desc, private):
    if not token or not name:
        return "Please provide a repository name and ensure you are authenticated."
    try:
        gh = GitHubClient(token)
        repo = gh.create_repository(name, desc, private)
        return f"Successfully created: **[{repo.full_name}]({repo.html_url})**"
    except Exception as e:
        return f"Error: {str(e)}"

# --- UI Design ---
with gr.Blocks(title="AGA - AI GitHub Assistant") as demo:
    # State management
    gh_session = gr.State()
    ai_session = gr.State()
    current_explorer_path = gr.State("") # Track current directory in explorer

    gr.Markdown("# AI GitHub Assistant (AGA)", elem_id="main-title")
    gr.Markdown("Transforming your GitHub workflow with professional-grade AI Intelligence.")

    with gr.Tab("Authentication"):
        with gr.Row():
            token_input = gr.Textbox(label="GitHub Personal Access Token",
                                   value=os.getenv("GITHUB_TOKEN", ""), placeholder="ghp_...")
            groq_input = gr.Textbox(label="Groq API Key",
                                  value=os.getenv("GROQ_API_KEY", ""), placeholder="gsk_...")
        auth_btn = gr.Button("Initialize Platform", variant="primary")
        auth_status = gr.Markdown("Status: Pending Authentication")

    with gr.Tab("Repo Manager"):
        gr.Markdown("### Repository Control Center")
        with gr.Row():
            refresh_btn = gr.Button("Sync with GitHub", variant="secondary")
        
        repo_table = gr.Dataframe(
            headers=["Full Name", "Visibility", "Stars", "Last Updated"], 
            interactive=False,
            label="Your Active Repositories (Select a row to explore)",
            datatype=["str", "str", "number", "str"]
        )
        
        gr.Markdown("---")
        gr.Markdown("### AI File Deployment Engine")
        
        with gr.Group():
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### 1. Target Repository")
                    repo_mode = gr.Radio(["Select Existing", "Manual Entry"], label="Input Method", value="Select Existing")
                    repo_select = gr.Dropdown(label="Selected Repo", choices=[], visible=True, interactive=True)
                    manual_repo_name = gr.Textbox(label="Repo Identifier (owner/repo)", placeholder="e.g. username/repo", visible=False)
                
                with gr.Column(scale=1):
                    gr.Markdown("#### 2. Navigation & Path")
                    explorer_table = gr.Dataframe(
                        headers=["Name", "Type", "Action"],
                        interactive=False,
                        label="File Explorer",
                        wrap=True
                    )
                    file_viewer_dropdown = gr.Dropdown(label="Quick View File Details", choices=[], interactive=True)
                    file_details_box = gr.Markdown("Select a file above to view metadata.")
                    target_path = gr.Textbox(label="Final Push Path", placeholder="e.g. folder/file.py")
                
                with gr.Column(scale=1):
                    gr.Markdown("#### 3. Deployment Settings")
                    file_uploader = gr.File(label="Upload File", file_count="multiple")
                    commit_msg = gr.Textbox(label="Commit Message", placeholder="Feat: Add new module via AGA")
                    push_btn = gr.Button("Deploy Code to GitHub", variant="primary", size="lg")

            with gr.Row():
                with gr.Column():
                    file_content = gr.Code(label="Code / File Content", language="python", lines=15)
            
            push_status = gr.HTML("<div style='text-align: center; padding: 10px; border-radius: 5px; background: #2d2d2d; border: 1px solid #444;'>Status: Waiting for deployment...</div>")

    with gr.Tab("Repo Creator"):
        gr.Markdown("### Create New Repository")
        with gr.Row():
            new_repo_name = gr.Textbox(label="Repository Name", placeholder="my-awesome-project")
            is_private = gr.Checkbox(label="Private Repository", value=True)
        new_repo_desc = gr.Textbox(label="Description (Optional)")
        create_btn = gr.Button("Create Repository on GitHub", variant="primary")
        create_status = gr.Markdown("")

    with gr.Tab("Deep Analyzer"):
        gr.Markdown("### Repository Health & Architecture Scan")
        with gr.Row():
            repo_url = gr.Textbox(label="Enter GitHub Repository URL", placeholder="https://github.com/username/repo", scale=4)
            model_choice = gr.Dropdown(
                choices=["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "mixtral-8x7b-32768"],
                label="AI Model",
                value="llama-3.3-70b-versatile",
                scale=1
            )
        analyze_btn = gr.Button("Start Deep Analysis", variant="primary")
        score_display = gr.Markdown("### Status: Waiting for input")
        report_display = gr.Textbox(label="Detailed AI Architectural Report", lines=20)

    with gr.Tab("Smart README"):
        gr.Markdown("### AI-Powered Documentation")
        proj_context = gr.Textbox(label="Project Details / File Structure", placeholder="Paste tree structure or summary here...", lines=8)
        style_choice = gr.Dropdown(choices=["professional", "open_source", "startup", "hackathon", "minimal"], 
                                 label="Readme Style Profile", value="professional")
        gen_btn = gr.Button("Generate Professional README", variant="primary")
        readme_output = gr.Markdown("---")
    
    gr.Markdown("---")
    with gr.Row():
        gr.Markdown("**Install AGA CLI:** `pip install aga-ai-github-assistant` &nbsp;&nbsp; [📦 View on PyPI](https://pypi.org/project/aga-ai-github-assistant/)")
        gr.Button("📋 Copy", size="sm").click(
            fn=None,
            js="() => { navigator.clipboard.writeText('pip install aga-ai-github-assistant'); }"
        )
    gr.Markdown("AGA Platform v1.2 | Powered by Llama 3.3 Intelligence", elem_id="footer")

    # --- Event Handlers ---
    auth_btn.click(
        authenticate, 
        inputs=[token_input, groq_input], 
        outputs=[auth_status, gh_session, ai_session]
    )

    refresh_btn.click(
        manage_repos,
        inputs=[token_input],
        outputs=[repo_table, repo_select]
    )

    # Explorer Logic
    repo_mode.change(
        update_repo_visibility,
        inputs=[repo_mode],
        outputs=[repo_select, manual_repo_name]
    )

    # Click a repo in the list to trigger exploration
    def select_repo_from_table(evt: gr.SelectData, token, table_data):
        import pandas as pd
        if isinstance(table_data, pd.DataFrame):
            data_list = table_data.values.tolist()
        else:
            data_list = table_data
            
        repo_name = data_list[evt.index[0]][0] # Always col 0 for full_name
        # Trigger folder fetch
        data, path, file_choices = get_repo_folders(token, repo_name, "")
        return repo_name, data, path, file_choices

    repo_table.select(
        select_repo_from_table,
        inputs=[token_input, repo_table],
        outputs=[repo_select, explorer_table, current_explorer_path, file_viewer_dropdown]
    )

    repo_select.change(
        get_repo_folders,
        inputs=[token_input, repo_select, current_explorer_path],
        outputs=[explorer_table, current_explorer_path, file_viewer_dropdown]
    )
    
    manual_repo_name.submit(
        get_repo_folders,
        inputs=[token_input, manual_repo_name, current_explorer_path],
        outputs=[explorer_table, current_explorer_path, file_viewer_dropdown]
    )

    def handle_explorer_click_with_dropdown(token, repo_full_name, current_path, table_data, evt: gr.SelectData):
        # Call the old handler logic but return the dropdown update too
        table, path, target = handle_explorer_click(token, repo_full_name, current_path, table_data, evt)
        # Refresh dropdown for new path
        _, _, dropdown_update = get_repo_folders(token, repo_full_name, path)
        return table, path, target, dropdown_update

    explorer_table.select(
        handle_explorer_click_with_dropdown,
        inputs=[token_input, repo_select, current_explorer_path, explorer_table],
        outputs=[explorer_table, current_explorer_path, target_path, file_viewer_dropdown]
    )

    file_viewer_dropdown.change(
        fetch_file_content,
        inputs=[token_input, repo_select, file_viewer_dropdown],
        outputs=[file_content, file_details_box]
    )

    file_uploader.change(
        handle_file_upload,
        inputs=[file_uploader, target_path],
        outputs=[file_content, target_path]
    )

    push_btn.click(
        handle_push,
        inputs=[token_input, manual_repo_name, repo_select, target_path, file_content, commit_msg],
        outputs=[push_status]
    )

    analyze_btn.click(
        run_analysis,
        inputs=[token_input, groq_input, repo_url, model_choice],
        outputs=[score_display, report_display]
    )

    gen_btn.click(
        generate_doc,
        inputs=[groq_input, proj_context, style_choice],
        outputs=[readme_output]
    )

    create_btn.click(
        handle_repo_creation,
        inputs=[token_input, new_repo_name, new_repo_desc, is_private],
        outputs=[create_status]
    )

if __name__ == "__main__":
    demo.launch(server_port=int(os.getenv("PORT", 7860)), share=True, theme=gr.themes.Soft())

