#!/bin/bash

# Azure deployment script for GitHub Agent
# Make sure you're logged in with: az login

# Configuration - UPDATE THESE VALUES
RG="agent-rg"
PLAN="agent-plan"
APP="github-agent-app-$(date +%s)"  # Adding timestamp for uniqueness
LOCATION="eastus"
GITHUB_REPO="https://github.com/arushitandon_microsoft/coder-agent-test"

echo "🚀 Deploying GitHub Agent to Azure..."
echo "Resource Group: $RG"
echo "App Name: $APP"
echo "GitHub Repo: $GITHUB_REPO"

# Step 1: Create Resource Group
echo "📦 Creating resource group..."
az group create \
  --name $RG \
  --location $LOCATION

# Step 2: Create App Service Plan
echo "📋 Creating app service plan..."
az appservice plan create \
  --name $PLAN \
  --resource-group $RG \
  --sku B1 \
  --is-linux

# Step 3: Create Web App with GitHub integration
echo "🌐 Creating web app..."
az webapp create \
  --resource-group $RG \
  --plan $PLAN \
  --name $APP \
  --runtime "PYTHON|3.10" \
  --deployment-source-url $GITHUB_REPO \
  --deployment-source-branch main

# Step 4: Configure app settings
echo "⚙️ Configuring app settings..."
az webapp config appsettings set \
  --resource-group $RG \
  --name $APP \
  --settings WEBSITES_CONTAINER_START_TIME_LIMIT=1800 \
             WEBSITE_RUN_FROM_PACKAGE=1 \
             SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Step 5: Set startup command
echo "🔧 Setting startup command..."
az webapp config set \
  --resource-group $RG \
  --name $APP \
  --startup-file "gunicorn --bind=0.0.0.0 --workers=4 github_agent_server:app"

echo "✅ Deployment complete!"
echo "🌐 Your app will be available at: https://$APP.azurewebsites.net"
echo ""
echo "⚠️  IMPORTANT: You still need to set your environment variables:"
echo "Run these commands with your actual API keys:"
echo ""
echo "az webapp config appsettings set \\"
echo "  --resource-group $RG \\"
echo "  --name $APP \\"
echo "  --settings OPENAI_API_KEY=\"your-openai-key-here\" \\"
echo "             GITHUB_TOKEN=\"your-github-token-here\""
