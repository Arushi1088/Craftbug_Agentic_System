#!/bin/bash
# GitHub Token Setup Script
# This script helps you configure your GitHub Personal Access Token

echo "🔧 GitHub Token Setup for Craftbug_Agentic_System"
echo "=================================================="
echo ""

echo "📋 Instructions to get your GitHub Personal Access Token:"
echo "1. Go to GitHub.com and sign in to your account (Arushi1088)"
echo "2. Click your profile picture → Settings"
echo "3. Scroll down to 'Developer settings' (bottom left)"
echo "4. Click 'Personal access tokens' → 'Tokens (classic)'"
echo "5. Click 'Generate new token' → 'Generate new token (classic)'"
echo "6. Give it a name like 'Craftbug_Agentic_System'"
echo "7. Select scopes: 'repo' (full control of private repositories)"
echo "8. Click 'Generate token'"
echo "9. Copy the token (you won't see it again!)"
echo ""

echo "🔑 Once you have your token, run one of these commands:"
echo ""
echo "Option 1 - Set token in remote URL:"
echo "git remote set-url origin https://YOUR_TOKEN@github.com/Arushi1088/Craftbug_Agentic_System.git"
echo ""
echo "Option 2 - Store token in credential helper:"
echo "git config --global credential.helper store"
echo "echo 'https://YOUR_TOKEN:x-oauth-basic@github.com' > ~/.git-credentials"
echo ""
echo "Option 3 - Use SSH (recommended for long-term):"
echo "ssh-keygen -t ed25519 -C 'your-email@example.com'"
echo "cat ~/.ssh/id_ed25519.pub"
echo "# Add this public key to GitHub Settings → SSH and GPG keys"
echo "git remote set-url origin git@github.com:Arushi1088/Craftbug_Agentic_System.git"
echo ""

echo "🚀 After setting up authentication, push your branch:"
echo "git push origin final-flow-enhanced-analysis"
echo ""

echo "💡 Current remote URL:"
git remote get-url origin
echo ""
