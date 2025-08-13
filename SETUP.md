# 🚀 Quick Setup Guide - Craftbug Agentic System

## ⚡ 5-Minute Setup

### 1. **Prerequisites Check**
```bash
# Check Python version (needs 3.11+)
python3 --version

# Check Node.js version (needs 16+)
node --version

# Check Git
git --version
```

### 2. **Clone & Setup**
```bash
# Clone the repository
git clone <your-repo-url>
cd Craftbug_Agentic_System

# Backend setup
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd web-ui
npm install
cd ..
```

### 3. **Environment Variables**
```bash
# Create environment file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
AZURE_DEVOPS_ORG=your_organization_name
AZURE_DEVOPS_PROJECT=your_project_name
AZURE_DEVOPS_PAT=your_personal_access_token
EOF
```

### 4. **Start the System**
```bash
# Terminal 1: Backend
python enhanced_fastapi_server.py

# Terminal 2: Frontend
cd web-ui && npm run dev
```

### 5. **Access the Application**
- 🌐 **Frontend**: http://localhost:8080
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

## 🔑 Required API Keys

### Google Gemini API
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Add to `.env` as `GEMINI_API_KEY`

### Azure DevOps PAT
1. Go to [Azure DevOps](https://dev.azure.com/)
2. User Settings → Personal Access Tokens
3. Create new token with full access
4. Add to `.env` as `AZURE_DEVOPS_PAT`

## 🎯 First Run

1. **Open Dashboard**: http://localhost:8080
2. **Start Analysis**: Enter a URL and select scenario
3. **View Report**: Check the generated analysis report
4. **Test AI Fix**: Try the automated code fixing feature

## 🆘 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Frontend won't start:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check environment variables
echo $GEMINI_API_KEY
echo $AZURE_DEVOPS_PAT
```

## 📚 Next Steps

- Read the [Complete Documentation](./CRAFTBUG_SYSTEM_DOCUMENTATION.md)
- Explore the [API Documentation](http://localhost:8000/docs)
- Check out the [Deployment Guide](./docs/DEPLOYMENT.md)

---

**Need help?** Open an issue on GitHub or check the troubleshooting section above.
