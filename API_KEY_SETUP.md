# 🔑 API Key Configuration Guide

## Quick Setup

### 1. **Get Your OpenAI API Key**
1. Go to https://platform.openai.com/api-keys
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)

### 2. **Configure the Key**

**Option A: Using .env file (Recommended)**
```bash
# Edit the .env file
nano .env

# Replace the placeholder with your actual key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Option B: Export in Terminal**
```bash
export OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Option C: Add to Shell Config (Persistent)**
```bash
# For Zsh (macOS default)
echo 'export OPENAI_API_KEY=sk-your-actual-api-key-here' >> ~/.zshrc
source ~/.zshrc

# For Bash
echo 'export OPENAI_API_KEY=sk-your-actual-api-key-here' >> ~/.bashrc
source ~/.bashrc
```

### 3. **Verify Configuration**

Run the setup script:
```bash
./setup-api-key.sh
```

Or test directly:
```bash
python3 -c "import os; print('API Key found:', bool(os.getenv('OPENAI_API_KEY')))"
```

### 4. **Restart Services**

After setting the API key, restart your services:
```bash
# Backend
python3 enhanced_fastapi_server.py

# Frontend (in another terminal)
cd web-ui && npm run dev
```

## Troubleshooting

### ❌ "API Key not found" Error

1. **Check Environment Variable**
   ```bash
   echo $OPENAI_API_KEY
   ```

2. **Verify .env File**
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

3. **Test Python Access**
   ```bash
   python3 -c "import os; print(os.getenv('OPENAI_API_KEY'))"
   ```

### ❌ VS Code Terminal Issues

If using VS Code, make sure the terminal inherits environment variables:
1. Restart VS Code after setting environment variables
2. Or set the key directly in VS Code's integrated terminal

### ❌ Different Terminal Windows

Make sure you set the API key in the **same terminal** where you run the UX Analyzer:
```bash
# Set the key
export OPENAI_API_KEY=sk-your-key-here

# Then run the analyzer in the same terminal
python3 enhanced_fastapi_server.py
```

## Files Overview

- **`.env`** - Local development configuration (not committed to git)
- **`.env.example`** - Template file (safe to commit)
- **`production.env`** - Production configuration template
- **`setup-api-key.sh`** - Interactive setup script

## Security Notes

- ✅ .env files are in .gitignore (API keys won't be committed)
- ✅ Use different keys for development and production
- ✅ Never share your API keys in public repositories
- ✅ Rotate keys regularly for security
