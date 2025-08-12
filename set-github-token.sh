#!/bin/bash

echo "🔑 GitHub Token Setup"
echo "===================="
echo ""

# Prompt for token (hidden input)
read -s -p "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

echo "✅ Token received. Setting up remote URL..."

# Set the remote URL with the token
git remote set-url origin "https://${GITHUB_TOKEN}@github.com/Arushi1088/Craftbug_Agentic_System.git"

echo "✅ Remote URL updated successfully!"
echo ""

# Verify the remote URL (hide the token)
echo "🔍 Current remote URL (token hidden):"
git remote get-url origin | sed 's/https:\/\/[^@]*@/https:\/\/***@/'
echo ""

echo "🚀 Now you can push your branch:"
echo "git push origin final-flow-enhanced-analysis"
echo ""

# Clear the token from memory
unset GITHUB_TOKEN
