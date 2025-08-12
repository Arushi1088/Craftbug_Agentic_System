#!/bin/bash

echo "🔑 Azure DevOps PAT Setup"
echo "========================"

# Prompt for PAT securely
read -s -p "Enter your Azure DevOps Personal Access Token: " ADO_PAT
echo ""

if [ -z "$ADO_PAT" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

# Set the environment variable
export ADO_PAT="$ADO_PAT"

# Also set other required ADO variables
export ADO_ORGANIZATION="nayararushi0668"
export ADO_PROJECT="CODER TEST"
export ADO_ENABLED="true"

echo "✅ PAT set successfully!"
echo "📋 Current ADO Configuration:"
echo "   Organization: $ADO_ORGANIZATION"
echo "   Project: $ADO_PROJECT"
echo "   Integration Enabled: $ADO_ENABLED"
echo "   PAT Configured: Yes"

echo ""
echo "🚀 To make this permanent, add these lines to your ~/.zshrc or ~/.bash_profile:"
echo "   export ADO_PAT='$ADO_PAT'"
echo "   export ADO_ORGANIZATION='$ADO_ORGANIZATION'"
echo "   export ADO_PROJECT='$ADO_PROJECT'"
echo "   export ADO_ENABLED='$ADO_ENABLED'"

echo ""
echo "🎯 ADO Integration is now active!"
echo "   - Issues will be automatically created as work items"
echo "   - 'Fix Now' buttons will navigate to the ADO board"
echo "   - Work items will appear in: https://dev.azure.com/nayararushi0668/CODER%20TEST/_workitems/recentlyupdated/"

# Clear the variable from memory for security
unset ADO_PAT
