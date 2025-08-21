# Jira Token Fix Guide

## Current Issue
Your current Jira token is a "Connect Session Auth Token" which is not compatible with Jira API access. You need a proper Jira API token.

## Quick Fix Steps

### Option 1: Atlassian Account API Token (Recommended)

1. **Go to Atlassian Account Settings**
   - Visit: https://id.atlassian.com/manage-profile/security/api-tokens
   - Sign in with your Atlassian account (the one you use for Jira)

2. **Create API Token**
   - Click "Create API token"
   - Give it a label: "Incident Response System"
   - Copy the generated token

3. **Update Your .env File**
   ```bash
   # Replace your current JIRA_TOKEN with the new one
   JIRA_TOKEN=your_new_atlassian_api_token_here
   
   # Add your email for basic auth
   JIRA_EMAIL=your_email@example.com
   ```

### Option 2: Jira Personal Access Token

1. **Go to Your Jira Instance**
   - Visit: https://mailtosimha.atlassian.net
   - Go to Profile → Personal Access Tokens

2. **Create Token**
   - Click "Create token"
   - Name: "Incident Response"
   - Copy the token

3. **Update Your .env File**
   ```bash
   JIRA_TOKEN=your_new_jira_pat_here
   ```

## Test Your New Token

After updating your token, run this test:

```bash
python3 test_jira_token_validation.py
```

## Expected Results

With the correct token, you should see:
- ✅ User authentication successful
- ✅ Projects retrieved
- ✅ Available project keys listed

## Current Status

- ❌ **Current Token**: Connect Session Auth Token (not compatible)
- 🔧 **Solution**: Get proper Jira API token
- 🎯 **Goal**: Enable Jira integration for incident response

## Next Steps

1. **Get the correct token** using one of the methods above
2. **Update your .env file** with the new token
3. **Test the token** with the validation script
4. **Proceed with integration** once token is working

## Support

If you continue to have issues:
- Check if you're using the right Atlassian account
- Verify your Jira instance type (Cloud vs Server)
- Try different authentication methods
- Contact your Jira admin if needed
