# Jira OAuth Quick Setup Guide

This guide helps you set up OAuth authentication for Jira using the provided authorization URL.

## Prerequisites

1. **Client Secret**: You need the client secret for the OAuth app with client ID `IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP`
2. **Python Dependencies**: Install required packages

## Setup Steps

### 1. Install Dependencies

```bash
pip install requests python-dotenv
```

### 2. Configure Environment

Copy the OAuth environment template:

```bash
cp env.oauth.example .env
```

Edit `.env` and add your client secret:

```bash
JIRA_OAUTH_CLIENT_SECRET=your_actual_client_secret_here
```

### 3. Run the OAuth Script

```bash
python jira_oauth_simple.py
```

The script will:

1. **Generate Authorization URL**: Uses the provided client ID and scopes
2. **Open Browser**: Automatically opens your browser to the authorization page
3. **Handle Callback**: Starts a local server on port 8080 to receive the authorization code
4. **Exchange Code**: Exchanges the authorization code for access and refresh tokens
5. **Display Tokens**: Shows the obtained tokens clearly

### 4. Expected Output

```
🚀 Jira OAuth Token Setup
============================================================
🔍 Step 1: Get Authorization Code
🔐 Jira OAuth Authorization Flow
==================================================
🔗 Authorization URL:
   https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP&scope=read%3Ajira-work%20manage%3Ajira-project%20manage%3Ajira-configuration%20read%3Ajira-user%20write%3Ajira-work%20manage%3Ajira-webhook%20manage%3Ajira-data-provider&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback&state=...&response_type=code&prompt=consent

🔐 State: [random_state_value]
🌐 Callback server started on port 8080

🌐 Opening browser for authorization...
⏳ Waiting for authorization...
✅ Authorization code received: [code_prefix]...

🔍 Step 2: Exchange Code for Access Token
🔄 Exchanging authorization code for tokens...
✅ Token exchange successful!
📄 Response: {
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600
}

🎉 TOKENS OBTAINED:
==================================================
🔑 Access Token: [your_access_token]
🔄 Refresh Token: [your_refresh_token]
📋 Token Type: Bearer
⏰ Expires In: 3600 seconds
==================================================

💾 Tokens saved to environment variables:
   JIRA_OAUTH_ACCESS_TOKEN
   JIRA_OAUTH_REFRESH_TOKEN

🎊 SUCCESS! OAuth tokens obtained successfully!
🚀 Ready to use with Jira MCP integration!

📋 Usage Example:
   # Add to your .env file:
   JIRA_OAUTH_ACCESS_TOKEN=[your_access_token]
   JIRA_OAUTH_REFRESH_TOKEN=[your_refresh_token]
```

## Troubleshooting

### Port 8080 Already in Use
If port 8080 is already in use, modify the script to use a different port:

```python
# In jira_oauth_simple.py, change:
server, auth_code_queue = self.start_callback_server(port=8081)
```

### Authorization Timeout
- Make sure you complete the authorization within 5 minutes
- Check that your browser can access the authorization URL
- Ensure the redirect URI matches exactly: `http://localhost:8080/callback`

### Token Exchange Fails
- Verify your client secret is correct
- Check that the authorization code hasn't expired (they expire quickly)
- Ensure the redirect URI matches between authorization and token exchange

## Using the Tokens

Once you have the tokens, you can use them with the existing MCP integration:

```python
# The tokens are automatically saved to environment variables
# You can use them in your existing scripts:

import os
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv("JIRA_OAUTH_ACCESS_TOKEN")
refresh_token = os.getenv("JIRA_OAUTH_REFRESH_TOKEN")

# Use with MCP client
headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}
```

## Security Notes

- Keep your client secret secure
- Access tokens expire (typically 1 hour)
- Refresh tokens can be used to get new access tokens
- Store tokens securely in your `.env` file
- Never commit tokens to version control
