# Free AI Models for FindingExcellence PRO

## Overview

FindingExcellence PRO is configured to use free AI models from OpenRouter by default, allowing you to test and develop the application without requiring credits or paid API keys.

## Available Free Models

### General Purpose Models
- **`deepseek/deepseek-r1:free`** - Primary free model for text processing
  - Context: 128K tokens
  - Good for: Document analysis, text processing, general AI tasks
  - Limitations: May be slower than paid models

- **`google/gemini-2.0-flash-exp:free`** - Alternative free model
  - Context: 1M tokens
  - Good for: Longer documents, complex queries
  - Note: Experimental model, may have occasional downtime

### Vision Models (for future image/PDF OCR features)
- **`google/gemini-2.0-flash-exp:free`** - Supports image input
  - Good for: Document OCR, image analysis
  - Limitations: Free tier may have rate limits

## Model Fallback System

The application includes an intelligent fallback system:

1. **Primary**: `deepseek/deepseek-r1:free`
2. **Fallback**: `google/gemini-2.0-flash-exp:free`
3. **Secondary**: Other available free models

If one free model fails or is rate-limited, the system automatically tries the next available free model.

## Configuration

### Environment Variables
```env
# Free model configuration (default)
OPENROUTER_MODEL=deepseek/deepseek-r1:free
OPENROUTER_TEMPERATURE=0.3
OPENROUTER_MAX_TOKENS=2000
```

### Model Selection Priority
1. **Free models first** - Always tries free options before paid
2. **Performance optimized** - Balances speed and quality
3. **Cost effective** - Zero cost for development and testing

## Usage Limits

### Free Model Limitations
- **Rate Limits**: Varies by model, typically 5-10 requests per minute
- **Token Limits**: 2,000 tokens per request (configurable)
- **Availability**: Models may occasionally be unavailable
- **Speed**: Response times may be slower than paid models

### Best Practices
1. **Batch requests** when possible to avoid rate limits
2. **Use smaller inputs** to stay within token limits
3. **Monitor responses** for quality and adjust prompts as needed
4. **Test thoroughly** as free models may have different behavior than paid ones

## Upgrading to Paid Models

When ready to upgrade for production use:

### Popular Paid Options
- `openai/gpt-4o-mini` - Fast, cost-effective
- `anthropic/claude-3.5-sonnet` - High quality, good for complex tasks
- `google/gemini-2.0-flash` - Balanced performance

### Configuration Changes
```env
# Paid model configuration
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_TEMPERATURE=0.7
OPENROUTER_MAX_TOKENS=4000
```

## Troubleshooting

### Common Issues

#### Model Not Responding
- Check if the free model is temporarily unavailable
- Wait a few minutes and retry
- The system should automatically fall back to alternative models

#### Rate Limit Errors
- Reduce request frequency
- Implement request queuing in your code
- Consider upgrading to paid models for higher limits

#### Poor Quality Responses
- Adjust the temperature setting (0.1-0.5 for more consistent results)
- Improve your prompt engineering
- Try alternative free models

### Monitoring
- Check application logs for model selection and performance
- Monitor token usage and costs (should be $0.00 with free models)
- Test with different document types to ensure compatibility

## Cost Management

### Free Tier Benefits
- **Zero cost** for all AI operations
- **Unlimited testing** during development
- **Multiple model options** for redundancy

### Cost Monitoring
Even with free models, it's good practice to monitor usage:
```python
# Usage summary (should show $0.00 cost)
usage = ai_client.get_usage_summary()
print(f"Total cost: ${usage['total_cost_usd']}")
```

## Support

If you encounter issues with free models:
1. Check OpenRouter status page for model availability
2. Review the application logs for specific error messages
3. Try switching to alternative free models
4. Consider temporary use of paid models for critical testing

---

**Last Updated**: October 2025  
**OpenRouter Free Models**: Subject to change and availability  
**Recommended**: Start with free models, upgrade as needed for production
