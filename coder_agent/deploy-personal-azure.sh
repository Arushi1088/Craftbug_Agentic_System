#!/bin/bash

# Personal Azure deployment script
# Run this AFTER creating the Web App in Azure Portal

# Configuration - UPDATE THESE VALUES
RG="github-agent-rg"
APP="coderfixagent"  # Use the same name from your portal
GITHUB_REPO="https://github.com/arushitandon_microsoft/coder-agent-test"

echo "🔧 Configuring your Azure Web App: $APP"

# Enable basic authentication
echo "📝 Enabling basic authentication..."
az webapp auth update \
  --resource-group $RG \
  --name $APP \
  --enabled true

# Configure GitHub deployment
echo "📦 Setting up GitHub deployment..."
az webapp deployment source config \
  --resource-group $RG \
  --name $APP \
  --repo-url $GITHUB_REPO \
  --branch main \
  --manual-integration

# Configure app settings for Python
echo "⚙️ Configuring Python runtime..."
az webapp config appsettings set \
  --resource-group $RG \
  --name $APP \
  --settings WEBSITES_CONTAINER_START_TIME_LIMIT=1800 \
             WEBSITE_RUN_FROM_PACKAGE=1 \
             SCM_DO_BUILD_DURING_DEPLOYMENT=true \
             FLASK_APP=github_agent_server.py

# Set startup command
echo "🚀 Setting startup command..."
az webapp config set \
  --resource-group $RG \
  --name $APP \
  --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 github_agent_server:app"

echo "✅ Configuration complete!"
echo "🌐 Your app will be available at: https://$APP.azurewebsites.net"
echo ""
echo "⚠️  NEXT STEPS:"
echo "1. Add your environment variables in Azure Portal:"
echo "   - Go to Configuration → Application Settings"
echo "   - Add: OPENAI_API_KEY = your-openai-key"
echo "   - Add: GITHUB_TOKEN = your-github-token"
echo "2. Wait 2-3 minutes for deployment to complete"
echo "3. Test your app!"
