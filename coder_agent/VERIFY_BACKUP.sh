#!/bin/bash

echo "🔍 BUGFIX2CODER Backup Verification Script"
echo "==========================================="
echo ""

# Check if we're in the right directory
if [[ ! -f "buggy_ecommerce_app.py" ]]; then
    echo "❌ Error: Not in BUGFIX2CODER directory"
    exit 1
fi

echo "✅ Directory Check: In BUGFIX2CODER folder"

# Check virtual environment
if [[ -d ".venv" ]]; then
    echo "✅ Virtual Environment: Found"
else
    echo "❌ Virtual Environment: Missing"
fi

# Check Gemini CLI
if [[ -x "./gemini" ]]; then
    echo "✅ Gemini CLI: Executable"
else
    echo "❌ Gemini CLI: Not executable"
fi

# Check git repository
if [[ -d ".git" ]]; then
    echo "✅ Git Repository: Present"
    COMMITS=$(git log --oneline | wc -l | tr -d ' ')
    echo "   - Commits: $COMMITS"
else
    echo "❌ Git Repository: Missing"
fi

# Check key files
FILES=("azure-pipelines.yml" "requirements.txt" "ecommerce.db" "templates/cart.html" "AI_SELF_HEALING_AGENT_COMPLETE_GUIDE.md")
for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ Key File: $file"
    else
        echo "❌ Missing File: $file"
    fi
done

echo ""
echo "🎉 Backup verification complete!"
echo "📁 Location: $(pwd)"
echo "📊 Total files: $(find . -type f | wc -l | tr -d ' ')"
echo "💾 Total size: $(du -sh . | cut -f1)"
echo ""
echo "🚀 Ready for integration with another project!"
