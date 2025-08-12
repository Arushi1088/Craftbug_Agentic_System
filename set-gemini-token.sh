#!/bin/bash
echo "🔑 Gemini API Token Setup"
echo "========================"
read -s -p "Enter your Gemini API Token: " GEMINI_TOKEN
echo ""
if [ -z "$GEMINI_TOKEN" ]; then echo "❌ No token provided. Exiting."; exit 1; fi
export GEMINI_TOKEN="$GEMINI_TOKEN"
echo "✅ Gemini token set successfully!"
echo ""
echo "📋 Current Configuration:"
echo "   Gemini Token: Set"
echo "   ADO PAT: $([ -n "$ADO_PAT" ] && echo "Set" || echo "Not Set")"
echo "   ADO Organization: $ADO_ORGANIZATION"
echo "   ADO Project: $ADO_PROJECT"
echo ""
echo "🚀 To make this permanent, add these lines to your ~/.zshrc or ~/.bash_profile:"
echo "   export GEMINI_TOKEN='$GEMINI_TOKEN'"
echo ""
echo "🎯 Coder Agent is now ready!"
echo "   - AI-powered fixes will work with real Gemini API"
echo "   - Fallback to simulation mode if token is not set"
echo "   - Check mock apps after fixes to see changes"
unset GEMINI_TOKEN
