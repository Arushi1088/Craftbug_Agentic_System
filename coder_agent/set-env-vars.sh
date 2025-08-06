#!/bin/bash

# Environment variables setup script
# Run this AFTER the main deployment

# Configuration - UPDATE THESE VALUES
RG="agent-rg"
APP="github-agent-app-$(date +%s)"  # Use the same timestamp as deployment

# Read from your .env file (more secure than hardcoding)
if [ -f ".env" ]; then
    export $(cat .env | xargs)
    
    echo "🔐 Setting environment variables from .env file..."
    
    az webapp config appsettings set \
      --resource-group $RG \
      --name $APP \
      --settings OPENAI_API_KEY="$OPENAI_API_KEY" \
                 GITHUB_TOKEN="$GITHUB_TOKEN"
    
    echo "✅ Environment variables set successfully!"
else
    echo "❌ .env file not found. Please create it with your API keys."
    echo "Or set variables manually:"
    echo ""
    echo "az webapp config appsettings set \\"
    echo "  --resource-group $RG \\"
    echo "  --name $APP \\"
    echo "  --settings OPENAI_API_KEY=\"your-key\" GITHUB_TOKEN=\"your-token\""
fi
