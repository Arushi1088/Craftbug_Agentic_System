import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from github import Github

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["*"])

# Initialize GitHub client
github_token = os.getenv("GITHUB_TOKEN")
if github_token:
    gh = Github(github_token)
else:
    gh = None
    print("Warning: GITHUB_TOKEN not found in environment variables")

@app.route('/')
def home():
    return """
    <h2>GitHub Agent Server</h2>
    <p>Server is running successfully!</p>
    <p>POST to /agent with {"command": "your command"} to modify GitHub repository</p>
    """

@app.route('/agent', methods=['POST'])
def handle_command():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        cmd = data.get("command", "").strip()
        if not cmd:
            return jsonify({"error": "Please provide a command"}), 400
        
        if not gh:
            return jsonify({"error": "GitHub token not configured"}), 500
            
        # Simple response for now
        return jsonify({"result": f"Command received: {cmd}"})
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
