# 🚀 PRODUCTION SETUP GUIDE
# Complete guide for configuring production credentials

## 📋 PREREQUISITES
- [ ] Azure DevOps account with project access
- [ ] Google AI Studio account (for Gemini API)
- [ ] GitHub account (optional)
- [ ] Git repository initialized

## 🔐 STEP-BY-STEP CREDENTIAL SETUP

### 1️⃣ **Azure DevOps Setup**
```bash
# 1. Visit Azure DevOps
https://dev.azure.com/[YOUR_ORG]

# 2. Go to User Settings → Personal Access Tokens
https://dev.azure.com/[YOUR_ORG]/_usersSettings/tokens

# 3. Create New Token with these scopes:
✅ Work Items (Read & Write)
✅ Code (Read) 
✅ Project and Team (Read)

# 4. Copy the token and update .env:
ADO_ORG=your-organization
ADO_PROJECT=your-project-name
ADO_TOKEN=pat_token_here
```

### 2️⃣ **Google Gemini AI Setup**
```bash
# 1. Visit Google AI Studio
https://makersuite.google.com/app/apikey

# 2. Create new API key for Gemini Pro

# 3. Update .env:
GEMINI_API_KEY=your_gemini_key_here
```

### 3️⃣ **GitHub Setup (Optional)**
```bash
# 1. Visit GitHub Personal Access Tokens
https://github.com/settings/tokens

# 2. Create token with 'repo' scope

# 3. Update .env:
GITHUB_TOKEN=your_github_token
GITHUB_REPO_OWNER=your-username
GITHUB_REPO_NAME=your-repo-name
```

### 4️⃣ **Gemini CLI Installation**
```bash
# Install Gemini CLI (choose one method):

# Method 1: pip install (if available)
pip install gemini-cli

# Method 2: Manual installation
# Download from: https://github.com/google/gemini-cli
# Add to PATH

# Verify installation:
gemini --help
```

### 5️⃣ **Test Production Setup**
```bash
# 1. Update .env with real credentials
cp .env.production.template .env
# Edit .env with your actual credentials

# 2. Test UX Analyzer (keep running)
cd ../
uvicorn fastapi_server:app --reload --port 8002

# 3. Test orchestrator (new terminal)
cd orchestrator/
python main.py

# 4. Check ADO tickets created
# Visit: https://dev.azure.com/[YOUR_ORG]/[PROJECT]/_workitems
```

## ✅ **PRODUCTION READINESS CHECKLIST**

### Required for Basic Functionality:
- [ ] ADO_ORG set to real organization
- [ ] ADO_PROJECT set to real project  
- [ ] ADO_TOKEN set to valid PAT
- [ ] UX Analyzer running on port 8002

### Required for AI Fixes:
- [ ] GEMINI_API_KEY set to valid key
- [ ] Gemini CLI installed and in PATH
- [ ] FRONTEND_PATH points to source files

### Required for Git Integration:
- [ ] AUTO_COMMIT_ENABLED=true
- [ ] AUTO_PUSH=true  
- [ ] Git repository initialized
- [ ] Git remote configured

### Optional Enhancements:
- [ ] GITHUB_TOKEN for GitHub integration
- [ ] SLACK_WEBHOOK_URL for notifications
- [ ] EMAIL_NOTIFICATIONS configured

## 🎯 **VALIDATION TESTS**

### Test 1: ADO Connection
```python
from ado_client import AzureDevOpsClient
client = AzureDevOpsClient()
assert client.test_connection() == True
```

### Test 2: Gemini CLI
```bash
gemini --help
# Should show usage information
```

### Test 3: Full Pipeline
```bash
python main.py
# Should create real ADO tickets
```

## 🔒 **SECURITY BEST PRACTICES**

1. **Never commit .env to Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use environment-specific .env files**
   ```bash
   .env.development
   .env.staging  
   .env.production
   ```

3. **Rotate tokens regularly**
   - ADO PATs: 90 days max
   - API keys: Every 6 months

4. **Limit token scopes**
   - Only grant minimum required permissions
   - Review token usage regularly

## 🚨 **TROUBLESHOOTING**

### ADO Authentication Fails (203)
- Check organization name spelling
- Verify project exists and you have access
- Regenerate PAT with correct scopes

### Gemini CLI Not Found
- Check PATH includes Gemini CLI location
- Try absolute path in GEMINI_CLI_PATH
- Verify installation: `which gemini`

### Git Auto-Commit Fails
- Check repository is initialized: `git status`
- Verify remote configured: `git remote -v`
- Check permissions for push access

## 📞 **SUPPORT**

If you encounter issues:
1. Check logs in `orchestrator/logs/`
2. Verify all .env variables are set
3. Test each component individually
4. Review ADO/GitHub/Google AI quota limits
