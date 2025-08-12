#!/bin/bash

# Azure DevOps Integration Setup Script
echo "🔧 Setting up Azure DevOps Integration"
echo "======================================"

# Set ADO organization and project
export ADO_ORGANIZATION="nayararushi0668"
export ADO_PROJECT="CODER TEST"

# Enable ADO integration
export ADO_ENABLED="true"

# Check if PAT is already set
if [ -z "$ADO_PAT" ]; then
    echo "⚠️  ADO_PAT not set. You'll need to set your Azure DevOps Personal Access Token:"
    echo "   export ADO_PAT='your-personal-access-token'"
    echo ""
    echo "   To get a PAT:"
    echo "   1. Go to https://dev.azure.com/nayararushi0668/_usersSettings/tokens"
    echo "   2. Create a new token with 'Work Items (read, write)' permissions"
    echo "   3. Copy the token and set it as ADO_PAT"
else
    echo "✅ ADO_PAT is already set"
fi

echo ""
echo "📋 Current ADO Configuration:"
echo "   Organization: $ADO_ORGANIZATION"
echo "   Project: $ADO_PROJECT"
echo "   Integration Enabled: $ADO_ENABLED"
echo "   PAT Configured: $([ -n "$ADO_PAT" ] && echo "Yes" || echo "No")"

echo ""
echo "🚀 ADO Integration is ready!"
echo "   Issues will be automatically created as work items in Azure DevOps"
echo "   'Fix Now' buttons will navigate to the ADO board"
