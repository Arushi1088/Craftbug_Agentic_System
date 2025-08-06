#!/bin/bash
# Azure DevOps Self-Hosted Agent Setup Script

echo "=== Azure DevOps Self-Hosted Agent Setup ==="
echo ""

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS - using macOS agent"
    AGENT_URL="https://vstsagentpackage.azureedge.net/agent/3.243.1/vsts-agent-osx-x64-3.243.1.tar.gz"
    AGENT_FILE="vsts-agent-osx-x64-3.243.1.tar.gz"
else
    echo "Detected Linux - using Linux agent"
    AGENT_URL="https://vstsagentpackage.azureedge.net/agent/3.243.1/vsts-agent-linux-x64-3.243.1.tar.gz"
    AGENT_FILE="vsts-agent-linux-x64-3.243.1.tar.gz"
fi

# Create agent directory
echo "Creating agent directory..."
mkdir -p ~/azagent && cd ~/azagent

# Download agent
echo "Downloading Azure DevOps agent..."
curl -O "$AGENT_URL"

# Extract
echo "Extracting agent..."
tar zxvf "$AGENT_FILE"

echo ""
echo "=== Agent downloaded and extracted ==="
echo ""
echo "Next steps:"
echo "1. Get your ADO_PAT token from .env file"
echo "2. Run the configuration:"
echo ""
echo "cd ~/azagent"
echo "./config.sh --unattended \\"
echo "  --url https://dev.azure.com/nayararushi0668 \\"
echo "  --auth pat \\"
echo "  --token YOUR_ADO_PAT \\"
echo "  --pool SelfHosted \\"
echo "  --agent \"my-selfhosted-agent\" \\"
echo "  --work _work"
echo ""
echo "3. Start the agent:"
echo "./run.sh"
echo ""
echo "Your ADO_PAT from .env file:"
