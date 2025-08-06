# github_agent_server.py - Enhanced with Azure DevOps Integration
import os
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from github import Github
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_1.work_item_tracking import WorkItemTrackingClient

# Load environment variables
load_dotenv()

# Azure DevOps client initialization
ADO_ORG_URL = os.getenv("ADO_ORGANIZATION_URL")
ADO_PROJECT = os.getenv("ADO_PROJECT")
ADO_PAT = os.getenv("ADO_PAT")

# Initialize ADO connection
creds = BasicAuthentication("", ADO_PAT)
ado_conn = Connection(base_url=ADO_ORG_URL, creds=creds) if ADO_PAT else None
wit_client = ado_conn.clients.get_work_item_tracking_client() if ado_conn else None

# Flask app
app = Flask(__name__)
CORS(app, origins=["*"])

# ADO Tool Functions
def fetch_ado_bug(bug_id: int) -> str:
    """Fetches title & description of an ADO bug by its ID."""
    try:
        if not wit_client:
            return "❌ ADO client not initialized"
        
        wi = wit_client.get_work_item(bug_id, expand="Fields")
        title = wi.fields.get("System.Title", "")
        desc = wi.fields.get("System.Description", "")
        state = wi.fields.get("System.State", "")
        work_item_type = wi.fields.get("System.WorkItemType", "")
        
        return f"🔖 {work_item_type} {bug_id}\nTitle: {title}\nState: {state}\nDescription:\n{desc}"
    except Exception as e:
        return f"❌ Error fetching work item {bug_id}: {str(e)}"

def update_ado_bug(bug_id: int, comment: str, state: str = "Done") -> str:
    """Adds a comment and updates state of an ADO bug."""
    try:
        if not wit_client:
            return "❌ ADO client not initialized"
        
        patch = [
            {"op": "add", "path": "/fields/System.History", "value": comment},
            {"op": "add", "path": "/fields/System.State", "value": state}
        ]
        
        wit_client.update_work_item(patch, id=bug_id)
        return f"✅ Work item {bug_id} moved to {state} with comment: {comment}"
    except Exception as e:
        return f"❌ Error updating work item {bug_id}: {str(e)}"

def create_ado_work_item(title, description="", work_item_type="Task"):
    """Create a work item in Azure DevOps"""
    try:
        if not wit_client:
            return "❌ ADO client not initialized"
        
        project = ADO_PROJECT or "CODER TEST"
        
        # Create work item
        document = [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "value": title
            }
        ]
        
        if description:
            document.append({
                "op": "add", 
                "path": "/fields/System.Description",
                "value": description
            })
        
        work_item = wit_client.create_work_item(
            document=document,
            project=project,
            type=work_item_type
        )
        
        return f"✅ Created {work_item_type} #{work_item.id}: {title}"
        
    except Exception as e:
        return f"❌ Error creating work item: {str(e)}"

def list_ado_work_items(limit=10):
    """List recent work items from Azure DevOps"""
    try:
        if not wit_client:
            return "❌ ADO client not initialized"
        
        project = ADO_PROJECT or "CODER TEST"
        
        # Query for work items
        wiql = f"""
        SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType]
        FROM WorkItems
        WHERE [System.TeamProject] = '{project}'
        ORDER BY [System.ChangedDate] DESC
        """
        
        query_result = wit_client.query_by_wiql({"query": wiql}, top=limit)
        
        if not query_result.work_items:
            return "📋 No work items found"
        
        # Get work item details
        work_item_ids = [item.id for item in query_result.work_items]
        work_items = wit_client.get_work_items(work_item_ids)
        
        result = "📋 Recent Work Items:\n"
        for item in work_items:
            result += f"#{item.id}: {item.fields['System.Title']} [{item.fields['System.State']}]\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error listing work items: {str(e)}"

def modify_github_file(command):
    """Modify the index.html file on GitHub based on command"""
    try:
        # Debug: Print environment info - v2.1
        token = os.getenv("GITHUB_TOKEN")
        print(f"GITHUB_TOKEN exists: {bool(token)}")
        print(f"GITHUB_TOKEN prefix: {token[:10] + '...' if token else 'None'}")
        print(f"Fresh client initialization fix active")
        
        # Create fresh GitHub client with current token
        gh = Github(token)
        
        # Get the repository
        print("Attempting to access repo: Arushi1088/Code-agent-test")
        repo = gh.get_repo("Arushi1088/Code-agent-test")
        
        # Get current file content
        print("Attempting to get index.html contents")
        file_content = repo.get_contents("index.html")
        current_content = file_content.decoded_content.decode('utf-8')
        print(f"Successfully retrieved file, size: {len(current_content)} bytes")
        
        # Apply modifications based on command
        updated_content = current_content
        cmd = command.lower()
        
        # Color changes - improved logic
        if "red" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #DC3545;', updated_content)
        elif "green" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #28A745;', updated_content)
        elif "blue" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #007BFF;', updated_content)
        elif "yellow" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #FFC107;', updated_content)
        elif "purple" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #6F42C1;', updated_content)
        elif "orange" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #FD7E14;', updated_content)
        elif "pink" in cmd:
            updated_content = re.sub(r'background-color:\s*[^;]+;', 'background-color: #E91E63;', updated_content)
        
        # Size changes
        if "larger" in cmd or "bigger" in cmd:
            updated_content = re.sub(r'padding:\s*[^;]+;', 'padding: 20px 40px;', updated_content)
            updated_content = re.sub(r'font-size:\s*[^;]+;', 'font-size: 24px;', updated_content)
        elif "smaller" in cmd or "tiny" in cmd:
            updated_content = re.sub(r'padding:\s*[^;]+;', 'padding: 8px 16px;', updated_content)
            updated_content = re.sub(r'font-size:\s*[^;]+;', 'font-size: 14px;', updated_content)
        
        # Text changes
        if "hello world" in cmd or ("hello" in cmd and "world" in cmd):
            updated_content = re.sub(r'<button[^>]*id="action-btn"[^>]*>([^<]*)</button>', 
                                   r'<button class="blue-button" id="action-btn">Hello World</button>', updated_content)
            updated_content = re.sub(r'<title>([^<]*)</title>', r'<title>Hello World</title>', updated_content)
        elif "click me" in cmd:
            updated_content = re.sub(r'<button[^>]*id="action-btn"[^>]*>([^<]*)</button>', 
                                   r'<button class="blue-button" id="action-btn">Click Me</button>', updated_content)
            updated_content = re.sub(r'<title>([^<]*)</title>', r'<title>Click Me</title>', updated_content)
        elif "submit" in cmd:
            updated_content = re.sub(r'<button[^>]*id="action-btn"[^>]*>([^<]*)</button>', 
                                   r'<button class="blue-button" id="action-btn">Submit</button>', updated_content)
            updated_content = re.sub(r'<title>([^<]*)</title>', r'<title>Submit</title>', updated_content)
        
        # Shape changes
        if "rounded" in cmd or "round" in cmd:
            updated_content = re.sub(r'border-radius:\s*[^;]+;', 'border-radius: 25px;', updated_content)
        elif "square" in cmd:
            updated_content = re.sub(r'border-radius:\s*[^;]+;', 'border-radius: 0px;', updated_content)
        
        # Check if content actually changed, but proceed anyway for user feedback
        content_changed = updated_content != current_content
        
        if content_changed:
            # Update the file on GitHub
            repo.update_file(
                path="index.html",
                message=f"Agent update: {command}",
                content=updated_content,
                sha=file_content.sha
            )
            
            # Also update the local file
            with open('index.html', 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return f"✅ Successfully updated both GitHub repo and local file with: {command}"
        else:
            # Even if no change, give positive feedback
            color_map = {
                "red": "#DC3545", "green": "#28A745", "blue": "#007BFF", 
                "yellow": "#FFC107", "purple": "#6F42C1", "orange": "#FD7E14", "pink": "#E91E63"
            }
            
            for color, hex_code in color_map.items():
                if color in cmd and hex_code in current_content:
                    return f"✅ Button is already {color}! Try a different color like: blue, green, purple, yellow, orange, pink"
            
            return f"✅ Processed command: {command}. Try: 'make it blue', 'make it larger', 'hello world'"
        
    except Exception as e:
        print(f"ERROR in modify_github_file: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        return f"❌ Error updating GitHub: {str(e)}"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/debug')
def debug_env():
    """Debug endpoint to check environment variables"""
    import os
    return jsonify({
        "github_token_exists": bool(os.getenv("GITHUB_TOKEN")),
        "github_token_prefix": os.getenv("GITHUB_TOKEN", "")[:10] + "..." if os.getenv("GITHUB_TOKEN") else "None",
        "openai_key_exists": bool(os.getenv("OPENAI_API_KEY")),
        "port": os.getenv("PORT", "Not set"),
        "ado_org_url": os.getenv("ADO_ORGANIZATION_URL", "Not set"),
        "ado_project": os.getenv("ADO_PROJECT", "Not set"),
        "ado_pat_exists": bool(os.getenv("ADO_PAT")),
        "all_env_vars": list(os.environ.keys())
    })

@app.route('/agent', methods=['POST'])
def handle_command():
    data = request.get_json()
    cmd = data.get("command", "").strip()
    
    if not cmd:
        return jsonify({"error": "Please provide a command"}), 400
    
    # Look for "Task <id>: <instruction>" or "Bug <id>: <instruction>"
    import re
    m = re.match(r'^(?:Task|Bug)\s+(\d+):\s*(.+)$', cmd, flags=re.IGNORECASE)
    if m:
        work_id = int(m.group(1))
        instruction = m.group(2)
        
        # Execute the 4-step workflow
        results = []
        
        # Step 1: Fetch ADO work item
        results.append(f"🔍 Fetching work item {work_id}...")
        ado_result = fetch_ado_bug(work_id)
        results.append(ado_result)
        
        # Step 2: Execute the GitHub instruction
        results.append(f"🔧 Executing: {instruction}")
        github_result = modify_github_file(instruction)
        results.append(github_result)
        
        # Step 3: Update ADO work item to Done
        results.append(f"✅ Marking work item {work_id} as Done...")
        update_result = update_ado_bug(work_id, f"Fixed by agent: {instruction}", "Done")
        results.append(update_result)
        
        # Return combined results
        combined_result = "\n".join(results)
        return jsonify({"result": combined_result})
    
    cmd_lower = cmd.lower()
    
    # Azure DevOps commands - simplified routing
    if cmd_lower.startswith("fetch bug") or cmd_lower.startswith("fetch task") or cmd_lower.startswith("fetch work item"):
        # e.g. "fetch bug 123"
        import re
        numbers = re.findall(r'\d+', cmd)
        if numbers:
            work_item_id = int(numbers[0])
            result = fetch_ado_bug(work_item_id)
        else:
            result = "❌ Please specify a work item ID (e.g., 'fetch bug 123')"
        return jsonify({"result": result})
    
    elif cmd_lower.startswith("update bug") or cmd_lower.startswith("update task") or cmd_lower.startswith("update work item"):
        # e.g. "update bug 123 done"
        import re
        numbers = re.findall(r'\d+', cmd)
        if numbers:
            work_item_id = int(numbers[0])
            if "done" in cmd_lower or "complete" in cmd_lower:
                result = update_ado_bug(work_item_id, "Updated by agent - marked as complete", "Done")
            elif "close" in cmd_lower:
                result = update_ado_bug(work_item_id, "Updated by agent - closed", "Closed")
            else:
                result = update_ado_bug(work_item_id, f"Updated by agent: {cmd}")
        else:
            result = "❌ Please specify a work item ID (e.g., 'update bug 123 done')"
        return jsonify({"result": result})
    
    elif cmd_lower.startswith("create task") or cmd_lower.startswith("add task"):
        # e.g. "create task Fix login issue"
        if "create task" in cmd_lower:
            title = cmd[cmd_lower.find("create task") + 12:].strip()
        else:
            title = cmd[cmd_lower.find("add task") + 9:].strip()
        
        if not title:
            title = "New task created by agent"
        
        result = create_ado_work_item(title, work_item_type="Task")
        return jsonify({"result": result})
    
    elif cmd_lower.startswith("create bug") or cmd_lower.startswith("add bug"):
        # e.g. "create bug Button not working"
        if "create bug" in cmd_lower:
            title = cmd[cmd_lower.find("create bug") + 11:].strip()
        else:
            title = cmd[cmd_lower.find("add bug") + 8:].strip()
        
        if not title:
            title = "New bug reported by agent"
        
        result = create_ado_work_item(title, work_item_type="Bug")
        return jsonify({"result": result})
    
    elif cmd_lower.startswith("list") and ("tasks" in cmd_lower or "work items" in cmd_lower):
        # e.g. "list tasks" or "list work items"
        result = list_ado_work_items()
        return jsonify({"result": result})
    
    # GitHub commands (existing functionality)
    else:
        result = modify_github_file(cmd)
        return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
