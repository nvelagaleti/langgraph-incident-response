# Jira API Token Setup Guide

## Current Issue
Your current Jira token is returning "Failed to parse Connect Session Auth Token", which indicates you're using a Connect Session token instead of a proper Jira API token.

## How to Get the Correct Jira API Token

### Option 1: Atlassian Account API Token (Recommended)

1. **Go to Atlassian Account Settings**
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens
   - Sign in with your Atlassian account

2. **Create API Token**
   - Click "Create API token"
   - Give it a label (e.g., "Incident Response System")
   - Copy the generated token

3. **Update Your .env File**
   ```bash
   JIRA_URL=https://mailtosimha.atlassian.net
   JIRA_TOKEN=your_new_api_token_here
   JIRA_EMAIL=your_email@example.com  # Add this for basic auth
   ```

### Option 2: Jira Personal Access Token (Jira Cloud)

1. **Go to Jira Settings**
   - In your Jira instance, go to Profile → Personal Access Tokens
   - Click "Create token"

2. **Configure Token**
   - Give it a name (e.g., "Incident Response")
   - Set appropriate scopes (read/write issues, projects)
   - Copy the generated token

### Option 3: Basic Authentication (Email + API Token)

If you have an Atlassian API token, you can use basic authentication:

```bash
# In your .env file
JIRA_URL=https://mailtosimha.atlassian.net
JIRA_EMAIL=your_email@example.com
JIRA_TOKEN=your_atlassian_api_token
```

## Testing Your Token

After updating your token, run this test:

```bash
python3 test_jira_token_validation.py
```

## Alternative Integration Approaches

### 1. Hybrid Approach (Recommended)
Since GitHub MCP is working, we can use:
- **GitHub**: MCP integration (working)
- **Jira**: Direct API integration (after token fix)

### 2. Direct API Integration
If MCP continues to fail, we can implement direct Jira API calls:
- Full control over Jira operations
- No MCP dependency
- Works with any Jira instance

### 3. Community MCP Server
We can explore community-maintained Jira MCP servers or deploy our own.

## Next Steps

1. **Get the correct Jira API token** using one of the methods above
2. **Update your .env file** with the new token
3. **Test the integration** with the validation script
4. **Choose integration approach** based on test results

## Current Status

- ✅ **GitHub MCP**: Working with GitHub Copilot MCP
- ❌ **Jira MCP**: Authentication issues (token format)
- 🔧 **Solution**: Fix Jira token, then implement hybrid approach

## Quick Test Commands

```bash
# Test current token
python3 jira_integration_solution.py

# Test with new token (after updating .env)
python3 test_jira_token_validation.py

# Test combined GitHub + Jira (after fixing Jira)
python3 test_combined_integration.py
```

## Support

If you continue to have issues:
1. Check your Jira instance type (Cloud vs Server)
2. Verify your account has API access permissions
3. Try different authentication methods
4. Consider using a different Jira project for testing
