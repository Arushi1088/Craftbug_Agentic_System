# Agent-Driven Button System

A simple web application that demonstrates an AI agent controlling UI elements through natural language commands.

## 🚀 Features

- **Interactive Button Control**: Change button colors, sizes, text, and shapes using natural language
- **Real-time Updates**: Page automatically refreshes to show changes
- **Simple Commands**: No complex syntax needed - just say what you want!
- **Flask Backend**: Lightweight server with CORS support
- **No API Keys Required**: Uses simple pattern matching (upgradeable to OpenAI)

## 🧪 Supported Commands

### Colors
- `"make it red"` / `"green"` / `"blue"` / `"yellow"` / `"purple"` / `"orange"` / `"pink"`

### Sizes  
- `"make it larger"` / `"bigger"`
- `"make it smaller"` / `"tiny"`

### Text Changes
- `"change text to hello world"`
- `"make it say press me"`
- `"change to submit"`
- `"make it click me"`

### Shapes
- `"make it rounded"` / `"round"`  
- `"make it square"`

### Combinations
- `"big red button"`
- `"small green rounded button"`

## 🛠️ Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/arushitandon_microsoft/coder-agent-test.git
   cd coder-agent-test
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-cors
   ```

4. **Run the server**
   ```bash
   python simple_agent_server.py
   ```

5. **Open the webpage**
   - Open `index.html` in your browser
   - Or visit: `file:///path/to/your/index.html`

## 📁 Files

- `index.html` - Interactive frontend with button and command input
- `simple_agent_server.py` - Flask server with pattern-matching agent
- `agent_server.py` - Advanced version with LangChain/OpenAI integration
- `agent.py` - Simple standalone color-changing script

## 🔧 Advanced Setup (Optional)

For OpenAI integration, create a `.env` file:
```env
OPENAI_API_KEY=your-api-key-here
```

Then use `agent_server.py` instead of `simple_agent_server.py`.

## 🎯 How It Works

1. User types command in the web interface
2. JavaScript sends command to Flask server via POST request
3. Server analyzes command and modifies `index.html` file
4. Page auto-refreshes to show changes
5. Magic! ✨

## 🤝 Contributing

Feel free to add more commands, improve the parsing logic, or enhance the UI!

---

*Built with ❤️ for demonstrating agent-driven UI interactions*
# Pipeline updated Mon Aug  4 23:57:01 IST 2025
