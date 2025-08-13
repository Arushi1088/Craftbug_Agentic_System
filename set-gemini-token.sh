#!/bin/bash

echo "🤖 Gemini API Token Setup"
echo "========================"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    touch .env
fi

# Prompt for token (hidden input)
read -s -p "Enter your Gemini API Key: " GEMINI_API_KEY
echo ""

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

echo "✅ Token received. Setting up environment..."

# Set environment variable for current session
export GEMINI_API_KEY="$GEMINI_API_KEY"

# Update .env file
if grep -q "GEMINI_API_KEY" .env; then
    # Update existing entry
    sed -i.bak "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$GEMINI_API_KEY/" .env
    echo "✅ Updated existing GEMINI_API_KEY in .env file"
else
    # Add new entry
    echo "GEMINI_API_KEY=$GEMINI_API_KEY" >> .env
    echo "✅ Added GEMINI_API_KEY to .env file"
fi

# Add to shell profile for persistence
SHELL_PROFILE=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_PROFILE="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_PROFILE="$HOME/.bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_PROFILE="$HOME/.bash_profile"
fi

if [ -n "$SHELL_PROFILE" ]; then
    # Check if already exists in profile
    if ! grep -q "GEMINI_API_KEY" "$SHELL_PROFILE"; then
        echo "" >> "$SHELL_PROFILE"
        echo "# Gemini API Key for Craftbug System" >> "$SHELL_PROFILE"
        echo "export GEMINI_API_KEY=\"$GEMINI_API_KEY\"" >> "$SHELL_PROFILE"
        echo "✅ Added GEMINI_API_KEY to $SHELL_PROFILE"
        echo "🔄 Please restart your terminal or run: source $SHELL_PROFILE"
    else
        echo "ℹ️  GEMINI_API_KEY already exists in $SHELL_PROFILE"
    fi
fi

echo ""
echo "🔍 Verifying setup..."

# Test the token by checking if it's accessible
if [ -n "$GEMINI_API_KEY" ]; then
    echo "✅ Environment variable set successfully"
    echo "🔑 Token length: ${#GEMINI_API_KEY} characters"
    
    # Test if the token works with a simple API call
    echo "🧪 Testing API connection..."
    TEST_RESPONSE=$(curl -s -X POST \
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=$GEMINI_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "contents": [{
                "parts": [{"text": "Hello, this is a test message."}]
            }]
        }' 2>/dev/null)
    
    if echo "$TEST_RESPONSE" | grep -q "error"; then
        echo "⚠️  API test failed. Please check your token."
        echo "   Response: $TEST_RESPONSE"
    else
        echo "✅ API connection successful!"
    fi
else
    echo "❌ Failed to set environment variable"
fi

echo ""
echo "🚀 Setup complete! You can now:"
echo "   - Run: python gemini_cli.py"
echo "   - Start the server: python enhanced_fastapi_server.py"
echo "   - Use AI-powered code fixing features"
echo ""

# Clear the token from memory
unset GEMINI_API_KEY

echo "💡 To use the token in new terminals, restart your terminal or run:"
echo "   source ~/.zshrc  # or ~/.bashrc"
echo ""
