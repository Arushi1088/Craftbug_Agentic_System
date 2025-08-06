# simple_agent_server.py
import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

# ─── Flask App ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app, origins=["*"])  # Allow all origins including file://

def modify_button(cmd):
    """Modify the button based on command"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        updated_content = content
        
        # Color changes
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
            updated_content = re.sub(r'padding:\s*[^;]+;', 'padding: 15px 30px;', updated_content)
            updated_content = re.sub(r'font-size:\s*[^;]+;', 'font-size: 20px;', updated_content)
        elif "smaller" in cmd or "tiny" in cmd:
            updated_content = re.sub(r'padding:\s*[^;]+;', 'padding: 5px 10px;', updated_content)
            updated_content = re.sub(r'font-size:\s*[^;]+;', 'font-size: 12px;', updated_content)
        
        # Text changes - more robust patterns
        if "hello world" in cmd or ("hello" in cmd and "world" in cmd):
            updated_content = re.sub(r'<button[^>]*id="action-btn"[^>]*>([^<]*)</button>', 
                                   r'<button class="blue-button" id="action-btn">Hello World</button>', updated_content)
            updated_content = re.sub(r'<button[^>]*id="send-cmd"[^>]*>([^<]*)</button>', 
                                   r'<button id="send-cmd" class="blue-button">Hello World</button>', updated_content)
        elif "press me" in cmd:
            updated_content = re.sub(r'<button[^>]*id="action-btn"[^>]*>([^<]*)</button>', 
                                   r'<button class="blue-button" id="action-btn">Press Me</button>', updated_content)
            updated_content = re.sub(r'<button[^>]*id="send-cmd"[^>]*>([^<]*)</button>', 
                                   r'<button id="send-cmd" class="blue-button">Press Me</button>', updated_content)
        elif "submit" in cmd:
            updated_content = re.sub(r'<button[^>]*id="action-btn"[^>]*>([^<]*)</button>', 
                                   r'<button class="blue-button" id="action-btn">Submit</button>', updated_content)
            updated_content = re.sub(r'<button[^>]*id="send-cmd"[^>]*>([^<]*)</button>', 
                                   r'<button id="send-cmd" class="blue-button">Submit</button>', updated_content)
        elif "click me" in cmd:
            updated_content = re.sub(r'<button[^>]*id="action-btn"[^>]*>([^<]*)</button>', 
                                   r'<button class="blue-button" id="action-btn">Click Me</button>', updated_content)
            updated_content = re.sub(r'<button[^>]*id="send-cmd"[^>]*>([^<]*)</button>', 
                                   r'<button id="send-cmd" class="blue-button">Click Me</button>', updated_content)
        elif "send to agent" in cmd:
            updated_content = re.sub(r'<button[^>]*id="send-cmd"[^>]*>([^<]*)</button>', 
                                   r'<button id="send-cmd" class="blue-button">Send to Agent</button>', updated_content)
        
        # Also fix any stray text in output area and title
        if "hello world" in cmd or ("hello" in cmd and "world" in cmd):
            updated_content = re.sub(r'<title>([^<]*)</title>', r'<title>Hello World</title>', updated_content)
            updated_content = re.sub(r'<pre id="agent-output">([^<]*)</pre>', r'<pre id="agent-output"></pre>', updated_content)
        elif "press me" in cmd:
            updated_content = re.sub(r'<title>([^<]*)</title>', r'<title>Press Me</title>', updated_content)
            updated_content = re.sub(r'<pre id="agent-output">([^<]*)</pre>', r'<pre id="agent-output"></pre>', updated_content)
        elif "click me" in cmd:
            updated_content = re.sub(r'<title>([^<]*)</title>', r'<title>Click Me</title>', updated_content)
            updated_content = re.sub(r'<pre id="agent-output">([^<]*)</pre>', r'<pre id="agent-output"></pre>', updated_content)
        elif "submit" in cmd:
            updated_content = re.sub(r'<title>([^<]*)</title>', r'<title>Submit</title>', updated_content)
            updated_content = re.sub(r'<pre id="agent-output">([^<]*)</pre>', r'<pre id="agent-output"></pre>', updated_content)
        if "rounded" in cmd or "round" in cmd:
            updated_content = re.sub(r'border-radius:\s*[^;]+;', 'border-radius: 25px;', updated_content)
        elif "square" in cmd:
            updated_content = re.sub(r'border-radius:\s*[^;]+;', 'border-radius: 0px;', updated_content)
        
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return f"✅ Button modified successfully!"
        
    except Exception as e:
        return f"❌ Error: {e}"

@app.route('/agent', methods=['POST'])
def handle_command():
    data = request.get_json()
    cmd = data.get("command", "").strip().lower()
    
    if not cmd:
        return jsonify({"error": "No command provided"}), 400
    
    # Process the command
    result = modify_button(cmd)
    
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
