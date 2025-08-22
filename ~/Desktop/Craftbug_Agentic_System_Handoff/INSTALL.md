# Quick Installation Guide

## 🚀 5-Minute Setup

### 1. Prerequisites
- Python 3.11+
- Node.js 16+
- OpenAI API key

### 2. Clone/Extract
```bash
# If you received this as a zip file, extract it
unzip Craftbug_Agentic_System_Handoff.zip
cd Craftbug_Agentic_System_Handoff
```

### 3. Environment Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your OpenAI API key
nano .env  # or use any text editor
```

### 5. Frontend Setup
```bash
cd web-ui
npm install
cd ..
```

### 6. Start the System
```bash
# Terminal 1: Start backend
python3 enhanced_fastapi_server.py

# Terminal 2: Start frontend
cd web-ui && npm run dev
```

### 7. Access Dashboard
Open http://127.0.0.1:8080 in your browser

## ✅ Verification

### Test the System
```bash
# Test screenshot flow
python3 test_screenshot_flow.py

# Test API health
curl http://127.0.0.1:8000/health
```

### Expected Output
- Backend: Running on http://127.0.0.1:8000
- Frontend: Running on http://127.0.0.1:8080
- Health check: `{"status":"healthy"}`

## 🐛 Common Issues

### Port Already in Use
```bash
# Kill existing processes
pkill -f "python3 enhanced_fastapi_server.py"
pkill -f "npm run dev"
```

### OpenAI Quota Issues
- Add billing to your OpenAI account
- Check usage at https://platform.openai.com/usage

### Permission Issues
```bash
# Fix file permissions
chmod +x *.py
chmod -R 755 web-ui/
```

## 📞 Need Help?

1. Check the main README.md for detailed documentation
2. Review test files for examples
3. Check OpenAI API status
4. Verify your .env file configuration

---

**Time to Setup**: ~5 minutes
**System Status**: ✅ Ready to use
