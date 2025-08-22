# AI Model Configuration Guide

## Overview
The Craftbug Agentic System now supports configurable AI models for analysis. You can switch between different OpenAI models based on your needs for cost, speed, and accuracy.

## Available Models

### GPT-4o-mini (Default - Recommended)
- **Model ID**: `gpt-4o-mini`
- **Cost**: ~$0.15/1M input tokens, ~$0.60/1M output tokens
- **Speed**: Fast
- **Accuracy**: High for most analysis tasks
- **Best for**: Cost-effective analysis with good accuracy

### GPT-4o (Full)
- **Model ID**: `gpt-4o`
- **Cost**: ~$2.50/1M input tokens, ~$10.00/1M output tokens
- **Speed**: Medium
- **Accuracy**: Highest
- **Best for**: When maximum accuracy is required

### GPT-4-turbo
- **Model ID**: `gpt-4-turbo-preview`
- **Cost**: ~$10.00/1M input tokens, ~$30.00/1M output tokens
- **Speed**: Medium
- **Accuracy**: High
- **Best for**: Legacy compatibility

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Set these environment variables before running the analysis:

```bash
# Set the model
export OPENAI_MODEL=gpt-4o-mini

# Optional: Configure other parameters
export OPENAI_TEMPERATURE=0.1
export OPENAI_MAX_TOKENS=2000

# Required: Your API key
export OPENAI_API_KEY=sk-your-api-key-here
```

### Method 2: .env File

Create a `.env` file in the project root:

```bash
# AI Model Configuration
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=2000

# API Key
OPENAI_API_KEY=sk-your-api-key-here
```

### Method 3: Direct Code Modification

You can also modify the model directly in the code files:

- `llm_enhanced_analyzer.py` - Line 35
- `dynamic_ux_analyzer.py` - Line 254

## Model Selection Guidelines

### Choose GPT-4o-mini when:
- ✅ Cost is a primary concern
- ✅ Fast analysis is needed
- ✅ Good accuracy is sufficient
- ✅ Processing large amounts of data

### Choose GPT-4o when:
- ✅ Maximum accuracy is required
- ✅ Analyzing complex visual issues
- ✅ Cost is not a major concern
- ✅ Processing smaller, critical datasets

### Choose GPT-4-turbo when:
- ✅ Legacy compatibility is needed
- ✅ Specific features not available in newer models

## Performance Comparison

| Model | Speed | Cost | Accuracy | Best Use Case |
|-------|-------|------|----------|---------------|
| gpt-4o-mini | ⚡⚡⚡ | 💰 | 🎯🎯🎯 | Daily analysis, cost optimization |
| gpt-4o | ⚡⚡ | 💰💰💰 | 🎯🎯🎯🎯 | Critical analysis, maximum accuracy |
| gpt-4-turbo | ⚡⚡ | 💰💰💰💰 | 🎯🎯🎯 | Legacy compatibility |

## Testing Your Configuration

You can test your model configuration by running:

```bash
python3 -c "
import os
print(f'Model: {os.getenv(\"OPENAI_MODEL\", \"gpt-4o-mini\")}')
print(f'Temperature: {os.getenv(\"OPENAI_TEMPERATURE\", \"0.1\")}')
print(f'Max Tokens: {os.getenv(\"OPENAI_MAX_TOKENS\", \"2000\")}')
print(f'API Key: {\"✅ Set\" if os.getenv(\"OPENAI_API_KEY\") else \"❌ Not set\"}')
"
```

## Troubleshooting

### Common Issues:

1. **Rate Limits**: If you hit rate limits, consider switching to GPT-4o-mini
2. **Cost Concerns**: Use GPT-4o-mini for cost optimization
3. **Accuracy Issues**: Switch to GPT-4o for better accuracy
4. **API Key Issues**: Ensure your API key is valid and has sufficient credits

### Error Messages:

- `"Request too large"`: Reduce `OPENAI_MAX_TOKENS` or switch to a model with higher limits
- `"Rate limit exceeded"`: Switch to GPT-4o-mini or wait before retrying
- `"Invalid API key"`: Check your `OPENAI_API_KEY` environment variable

## Current Configuration

The system is currently configured to use **GPT-4o-mini** by default for optimal cost-performance balance.
