# Production Setup Guide for Self-Healing Pipeline

## Overview
This guide walks you through upgrading the pipeline from simulation mode to full production functionality with real code changes, Git operations, and Azure DevOps work item management.

## Prerequisites
- ✅ Azure DevOps self-hosted agent (already configured)
- ✅ GitHub repository with pipeline YAML (already set up)
- ✅ Azure DevOps project with work items (CODER TEST project ready)

## Required Pipeline Variables

### 1. GitHub Personal Access Token (GITHUB_TOKEN)
**Purpose**: Allows the pipeline to push commits back to GitHub

**Steps to create**:
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
4. Copy the token (you won't see it again!)

**Add to Azure DevOps**:
1. Go to your pipeline → Edit → Variables
2. Add variable: `GITHUB_TOKEN`
3. **Mark as secret** ✅
4. Paste your GitHub token

### 2. Azure DevOps Personal Access Token (ADO_PAT)
**Purpose**: Allows the pipeline to update work item states

**Steps to create**:
1. Go to Azure DevOps → User Settings → Personal access tokens
2. Click "+ New Token"
3. Select scopes:
   - `Work Items` (Read & Write)
   - `Project and Team` (Read)
4. Copy the token

**Add to Azure DevOps**:
1. Go to your pipeline → Edit → Variables  
2. Add variable: `ADO_PAT`
3. **Mark as secret** ✅
4. Paste your Azure DevOps token

### 3. Azure Service Connection (Optional)
**Purpose**: For Azure CLI tasks to update work items

**Steps to create**:
1. Go to Project Settings → Service connections
2. Create new Azure Resource Manager connection
3. Use service principal (automatic)
4. Name it `DefaultAzureCredential`

## Testing the Enhanced Pipeline

### Test 1: Create a Real Work Item
1. Go to Azure DevOps → Boards → Work Items
2. Create a new Task: "Change button text to 'Enhanced'"
3. Note the Work Item ID (e.g., #15)

### Test 2: Run Pipeline with Real Parameters
```bash
az pipelines run --id 1 \
  --parameters PatchInstruction="change button text to Enhanced" WorkItemId=15
```

### Expected Results
✅ **GitHub**: New commit with your changes  
✅ **Branch**: Feature branch created (feature/patch-[BuildId])  
✅ **Files**: PATCH_LOG.md and simulated changes created  
✅ **Work Item**: Status changed to "Closed" with automated comment  

## Real Gemini CLI Integration

### Current State
The pipeline includes placeholder for Gemini CLI:
```yaml
# TODO: Replace with real Gemini CLI when available
# gemini patch --instruction "${{ parameters.PatchInstruction }}" --repo-path "$(Build.SourcesDirectory)"
```

### Production Upgrade
When Gemini CLI becomes available, replace the installation step:
```yaml
- script: |
    curl -sSL https://download.gemini.ai/cli/install.sh | bash
    gemini --version
  displayName: 'Install Gemini CLI'
```

And replace the patch application:
```yaml
- script: |
    gemini patch \
      --instruction "${{ parameters.PatchInstruction }}" \
      --repo-path "$(Build.SourcesDirectory)"
  displayName: 'Apply Real Gemini Patch'
```

## Monitoring & Troubleshooting

### Pipeline Logs
- Check "Apply Gemini Patch" step for Git operations
- Check "Update Azure DevOps Work Item" step for ADO integration
- Look for commit hashes and branch names in output

### Common Issues
1. **Git push fails**: Check GITHUB_TOKEN permissions
2. **Work item update fails**: Check ADO_PAT scopes
3. **Branch conflicts**: Pipeline creates unique branch names automatically

### Success Indicators
- ✅ New commits appear in GitHub
- ✅ Work items move to "Closed" state
- ✅ Pipeline logs show "✅ Changes pushed to GitHub"
- ✅ Work item comments include build details

## Next Steps
1. Set up the pipeline variables (GITHUB_TOKEN, ADO_PAT)
2. Test with a real work item
3. Monitor the first few runs for any issues
4. When Gemini CLI is available, upgrade the installation steps
5. Scale to additional repositories and teams

## Security Best Practices
- ⚠️ Always mark tokens as **secret** in pipeline variables
- 🔒 Use minimal required permissions for tokens
- 🔄 Rotate tokens periodically (every 90 days recommended)
- 📝 Document which pipelines use which tokens

Your self-healing development system is now ready for production! 🚀
