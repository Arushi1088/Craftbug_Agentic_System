# agent_server.py
import os
import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.agents import initialize_agent, Tool
from github import Github

# ─── Setup ─────────────────────────────────────────────────────────────────────
load_dotenv()  # expects OPENAI_API_KEY & GITHUB_TOKEN
llm = OpenAI(temperature=0)
gh = Github(os.getenv("GITHUB_TOKEN"))

# ─── GitHub file I/O tools ────────────────────────────────────────────────
def fetch_remote_file(args: dict) -> str:
    """
    args = {
      "owner": "<github-username or org>",
      "repo":  "<repo-name>",
      "path":  "<file-path>",
      "branch": "<branch-name (optional, default main)>"
    }
    """
    repo = gh.get_repo(f"{args['owner']}/{args['repo']}")
    branch = args.get("branch", "main")
    contents = repo.get_contents(args["path"], ref=branch)
    return contents.decoded_content.decode("utf-8")

def update_remote_file(args: dict) -> str:
    """
    args = {
      "owner":         "<github-username or org>",
      "repo":          "<repo-name>",
      "path":          "<file-path>",
      "branch":        "<branch-name (optional)>",
      "content":       "<new file contents>",
      "commit_message": "<your commit message>"
    }
    """
    repo = gh.get_repo(f"{args['owner']}/{args['repo']}")
    branch = args.get("branch", "main")
    # fetch the current SHA
    contents = repo.get_contents(args["path"], ref=branch)
    repo.update_file(
        path=args["path"],
        message=args["commit_message"],
        content=args["content"],
        sha=contents.sha,
        branch=branch
    )
    return f"✅ Committed `{args['path']}` on `{args['owner']}/{args['repo']}`"

# ─── Local tools (read/write/run_tests) as before ──────────────────────────
def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(args: dict) -> str:
    with open(args['path'], 'w', encoding='utf-8') as f:
        f.write(args['content'])
    return f"Wrote {len(args['content'])} chars to {args['path']}"

def run_tests(_: str) -> str:
    proc = subprocess.run(["npm", "test"], capture_output=True, text=True)
    return proc.stdout + proc.stderr

tools = [
    Tool(
        name="fetch_remote_file",
        func=fetch_remote_file,
        description="Fetches a file from GitHub. Pass a dict with keys: owner, repo, path, branch (optional)."
    ),
    Tool(
        name="update_remote_file", 
        func=update_remote_file,
        description="Commits a file to GitHub. Pass a dict with keys: owner, repo, path, branch, content, commit_message."
    ),
    Tool(
        name="read_file",
        func=read_file,
        description="Reads a local file. Pass the file path as a string."
    ),
    Tool(
        name="write_file",
        func=write_file,
        description="Writes to a local file. Pass a dict with keys: path, content."
    ),
    Tool(
        name="run_tests",
        func=run_tests,
        description="Runs npm test locally. Pass any string (ignored)."
    )
]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=False
)

# ─── Flask App ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins including file://

@app.route('/agent', methods=['POST'])
def handle_command():
    data = request.get_json()
    cmd = data.get("command", "").strip()
    if not cmd:
        return jsonify({"error": "Please provide a command"}), 400

    # Build the sequential prompt
    # 1. Fetch the target file from GitHub
    # 2. Instruct the agent to apply the user's command
    # 3. Commit it back to GitHub
    # 4. Also save locally
    prompt = f"""
    fetch_remote_file {{ "owner": "arushitandon_microsoft",
                         "repo":  "coder-agent-test",
                         "path":  "index.html",
                         "branch":"main" }}
    {cmd}
    update_remote_file {{ "owner": "arushitandon_microsoft",
                          "repo":  "coder-agent-test", 
                          "path":  "index.html",
                          "branch": "main",
                          "commit_message": "Agent update: {cmd}" }}
    write_file {{ "path": "index.html" }}
    """
    
    try:
        result = agent.run(prompt)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": f"Agent error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
