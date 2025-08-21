# Complete Jira OAuth Setup Guide

This guide provides a complete solution for setting up OAuth authentication with Jira using the provided authorization URL.

## 🎯 What This Solves

You have the authorization URL:
```
https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP&scope=read%3Ajira-work%20manage%3Ajira-project%20manage%3Ajira-configuration%20read%3Ajira-user%20write%3Ajira-work%20manage%3Ajira-webhook%20manage%3Ajira-data-provider&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback&state=${YOUR_USER_BOUND_VALUE}&response_type=code&prompt=consent
```

This guide helps you:
1. ✅ Get the authorization code automatically
2. ✅ Exchange the code for access and refresh tokens
3. ✅ Use the tokens with your existing MCP integration

## 📁 Files Created

- `jira_oauth_simple.py` - Main OAuth script
- `test_oauth_url.py` - Test URL generation
- `use_oauth_tokens.py` - Test token usage with MCP
- `env.oauth.example` - Environment template
- `JIRA_OAUTH_QUICK_SETUP.md` - Quick setup guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install requests python-dotenv
```

### 2. Set Up Environment

```bash
# Copy the OAuth environment template
cp env.oauth.example .env

# Edit .env and add your client secret
JIRA_OAUTH_CLIENT_SECRET=your_actual_client_secret_here
```

### 3. Run the OAuth Script

```bash
python3 jira_oauth_simple.py
```

The script will:
- 🔗 Generate the authorization URL (matching your provided URL)
- 🌐 Open your browser automatically
- 🔐 Handle the OAuth callback
- 🔄 Exchange the code for tokens
- 📋 Display the access and refresh tokens clearly

### 4. Expected Output

```
🚀 Jira OAuth Token Setup
============================================================
🔍 Step 1: Get Authorization Code
🔐 Jira OAuth Authorization Flow
==================================================
🔗 Authorization URL:
   https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP&scope=read%3Ajira-work%20manage%3Ajira-project%20manage%3Ajira-configuration%20read%3Ajira-user%20write%3Ajira-work%20manage%3Ajira-webhook%20manage%3Ajira-data-provider&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback&state=...&response_type=code&prompt=consent

🌐 Opening browser for authorization...
⏳ Waiting for authorization...
✅ Authorization code received: [code_prefix]...

🔍 Step 2: Exchange Code for Access Token
🔄 Exchanging authorization code for tokens...
✅ Token exchange successful!

🎉 TOKENS OBTAINED:
==================================================
🔑 Access Token: [your_access_token]
🔄 Refresh Token: [your_refresh_token]
📋 Token Type: Bearer
⏰ Expires In: 3600 seconds
==================================================

🎊 SUCCESS! OAuth tokens obtained successfully!
```

## 🔧 How It Works

### Authorization URL Generation

The script generates the exact same URL you provided:

```python
params = {
    "audience": "api.atlassian.com",
    "client_id": "IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP",
    "scope": "read:jira-work manage:jira-project manage:jira-configuration read:jira-user write:jira-work manage:jira-webhook manage:jira-data-provider",
    "redirect_uri": "http://localhost:8080/callback",
    "state": "[random_state]",
    "response_type": "code",
    "prompt": "consent"
}
```

### Token Exchange

After getting the authorization code, it exchanges it for tokens:

```python
data = {
    "grant_type": "authorization_code",
    "client_id": "IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP",
    "client_secret": "your_client_secret",
    "code": "authorization_code",
    "redirect_uri": "http://localhost:8080/callback"
}

response = requests.post("https://auth.atlassian.com/oauth/token", data=data)
```

## 🧪 Testing

### Test URL Generation

```bash
python3 test_oauth_url.py
```

This verifies that the authorization URL is generated correctly.

### Test Token Usage

```bash
python3 use_oauth_tokens.py
```

This tests the obtained tokens with MCP integration.

## 🔗 Integration with Existing Code

Once you have the tokens, you can use them with your existing MCP scripts:

### Update Your Environment

Add to your `.env` file:
```bash
JIRA_OAUTH_ACCESS_TOKEN=your_access_token_here
JIRA_OAUTH_REFRESH_TOKEN=your_refresh_token_here
```

### Use with MCP Client

```python
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

access_token = os.getenv("JIRA_OAUTH_ACCESS_TOKEN")

servers_config = {
    "jira": {
        "transport": "streamable_http",
        "url": "https://api.atlassian.com/mcp",
        "headers": {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    }
}

client = MultiServerMCPClient(servers_config)
```

## 🔄 Token Refresh

Access tokens expire (typically 1 hour). You can refresh them using the refresh token:

```python
def refresh_access_token(refresh_token, client_id, client_secret):
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    
    response = requests.post("https://auth.atlassian.com/oauth/token", data=data)
    return response.json()
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port 8080 Already in Use**
   - Change the port in `jira_oauth_simple.py`
   - Update the redirect URI in your OAuth app settings

2. **Authorization Timeout**
   - Complete authorization within 5 minutes
   - Check browser can access the authorization URL

3. **Token Exchange Fails**
   - Verify client secret is correct
   - Authorization codes expire quickly - run the script immediately after authorization

4. **MCP Connection Fails**
   - Check token is valid and not expired
   - Verify MCP server URL is correct

### Debug Mode

Add debug output by modifying the script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔒 Security Notes

- ✅ Keep client secret secure
- ✅ Store tokens in `.env` file (not in code)
- ✅ Never commit tokens to version control
- ✅ Access tokens expire - implement refresh mechanism
- ✅ Use HTTPS for all API calls

## 📚 Additional Resources

- [Atlassian OAuth Documentation](https://developer.atlassian.com/cloud/jira/platform/oauth-2-authorization-code-grants-3lo-for-apps/)
- [MCP Integration Guide](LANGCHAIN_MCP_SETUP.md)
- [Jira API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)

## 🎉 Success!

Once you've completed this setup, you'll have:

1. ✅ Working OAuth authentication with Jira
2. ✅ Access and refresh tokens
3. ✅ Integration with your existing MCP setup
4. ✅ Ready for production use with your incident response system

Your Jira OAuth setup is now complete and ready to use with the LangGraph incident response agent!
