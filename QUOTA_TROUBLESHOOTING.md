# OpenAI API Quota Troubleshooting

## Error: "You exceeded your current quota"

This error occurs when your OpenAI API account has reached its usage limits. Here's how to resolve it:

### Immediate Solutions

1. **Check Your Usage**
   - Visit [OpenAI Platform Usage](https://platform.openai.com/usage)
   - Review your current usage and billing details

2. **Upgrade Your Plan**
   - Go to [OpenAI Platform Billing](https://platform.openai.com/account/billing)
   - Add payment method or increase spending limits

3. **Wait for Reset**
   - Free tier quotas reset monthly
   - Paid tier quotas reset based on your billing cycle

### Application Behavior

When quota is exceeded, the application will:
- ✅ Continue to function normally
- ⚠️ Show user-friendly error messages
- 📊 Provide basic data analysis without AI
- 🔄 Automatically retry with exponential backoff

### Configuration Options

You can modify the behavior in `config.py`:

```python
# Retry settings
OPENAI_MAX_RETRIES = 3
OPENAI_BASE_DELAY = 1.0  # seconds

# Fallback mode
FALLBACK_MODE_ENABLED = True
```

### Environment Variables

Make sure your API key is properly set:

```bash
export OPEN_AI_KEY="sk-your-api-key-here"
```

### Testing Your Setup

Run this to check your configuration:

```python
from config import config
print(config.get_status_message())
```

### Alternative Solutions

1. **Use a Different Model**
   - Switch to `gpt-3.5-turbo` (cheaper)
   - Modify `OPENAI_MODEL` in `config.py`

2. **Implement Caching**
   - Cache responses for repeated questions
   - Reduce API calls

3. **Rate Limiting**
   - Implement request throttling
   - Use `MAX_REQUESTS_PER_MINUTE` setting

### Support

- [OpenAI Documentation](https://platform.openai.com/docs)
- [OpenAI Community](https://community.openai.com/)
- [Billing Support](https://help.openai.com/en/articles/6891831-error-code-429-you-exceeded-your-current-quota)
