# OAuth Setup Guide for Atlassian MCP

## Step-by-Step OAuth Setup

### Step 1: Create Atlassian App

1. **Go to Atlassian Developer Console**
   - Visit: https://developer.atlassian.com/console/myapps/
   - Sign in with your Atlassian account (the one you use for Jira)

2. **Create New App**
   - Click "Create app"
   - Choose "OAuth 2.0 (3LO)" integration
   - **App name**: "Incident Response MCP"
   - **App description**: "MCP integration for incident response automation"
   - Click "Create"

### Step 2: Configure OAuth Settings

1. **In your app dashboard, go to "OAuth 2.0 (3LO)" section**

2. **Add Authorization URL**
   - **Authorization URL**: `https://auth.atlassian.com/authorize`

3. **Add Token URL**
   - **Token URL**: `https://auth.atlassian.com/oauth/token`

4. **Add Redirect URI**
   - **Redirect URI**: `http://localhost:8080/callback`
   - Click "Add"

5. **Configure Scopes**
   - Click "Add scope"
   - Add these scopes one by one:
     - `read:jira-work`
     - `write:jira-work`
     - `read:jira-user`
     - `manage:jira-project`

### Step 3: Get Credentials

1. **Copy Client ID**
   - In your app dashboard, find the "Client ID"
   - Copy it to your clipboard

2. **Copy Client Secret**
   - Click "Show" next to "Client Secret"
   - Copy it to your clipboard

### Step 4: Update Environment Variables

1. **Open your .env file**
   ```bash
   nano .env
   ```

2. **Add OAuth credentials**
   ```bash
   # Add these lines to your .env file
   JIRA_OAUTH_CLIENT_ID=your_client_id_here
   JIRA_OAUTH_CLIENT_SECRET=your_client_secret_here
   JIRA_OAUTH_REDIRECT_URI=http://localhost:8080/callback
   ```

3. **Save the file**

### Step 5: Test OAuth Setup

1. **Run the OAuth implementation**
   ```bash
   python3 jira_oauth_implementation.py
   ```

2. **Follow the prompts**
   - The script will open your browser
   - Authorize the app
   - Complete the OAuth flow

## Expected Flow

1. **Script starts** → Opens browser for authorization
2. **Browser opens** → Atlassian authorization page
3. **You authorize** → Click "Allow" for the requested permissions
4. **Redirect happens** → Back to localhost:8080/callback
5. **Script continues** → Exchanges code for access token
6. **MCP client initializes** → Tests Jira operations

## Troubleshooting

### Common Issues:

1. **"Invalid redirect URI"**
   - Make sure the redirect URI in your app matches exactly: `http://localhost:8080/callback`

2. **"Invalid client"**
   - Check that your Client ID and Secret are correct
   - Make sure you copied them from the right app

3. **"Insufficient scope"**
   - Verify all required scopes are added to your app
   - Check the scope names are exactly as listed above

4. **"Port 8080 already in use"**
   - The script will automatically handle this
   - If it fails, try a different port by modifying the script

### Verification Steps:

1. **Check app configuration**
   - Go back to your app dashboard
   - Verify all settings are correct

2. **Test with curl** (optional)
   ```bash
   # Test authorization URL
   curl "https://auth.atlassian.com/authorize?audience=api.atlassian.com&client_id=YOUR_CLIENT_ID&scope=read:jira-work&redirect_uri=http://localhost:8080/callback&state=test&response_type=code&prompt=consent"
   ```

## Next Steps

After successful OAuth setup:

1. **Test the integration**
   ```bash
   python3 jira_oauth_implementation.py
   ```

2. **Integrate with LangGraph**
   - The OAuth tokens will be available for MCP integration
   - Update the LangGraph system to use OAuth tokens

3. **Production deployment**
   - Consider using environment variables for production
   - Implement token refresh logic for long-running applications

## Security Notes

- **Never commit OAuth credentials** to version control
- **Use environment variables** for all sensitive data
- **Rotate credentials** regularly
- **Monitor app usage** in Atlassian Developer Console

## Support

If you encounter issues:
1. Check the Atlassian Developer Console for app status
2. Verify all OAuth settings are correct
3. Check the script output for specific error messages
4. Ensure your Atlassian account has access to the Jira instance
