# Jira OAuth Setup for MCP

## Current Situation
You're correct! The Atlassian MCP server (`https://mcp.atlassian.com/v1/sse`) requires OAuth 2.0 setup with client credentials, not just a personal access token.

## Option 1: OAuth Setup for Atlassian MCP

### Step 1: Create Atlassian App
1. **Go to Atlassian Developer Console**
   - Visit: https://developer.atlassian.com/console/myapps/
   - Sign in with your Atlassian account

2. **Create New App**
   - Click "Create app"
   - Choose "OAuth 2.0 (3LO)" integration
   - Name: "Incident Response MCP"
   - Description: "MCP integration for incident response automation"

3. **Configure OAuth Settings**
   - **Authorization URL**: `https://auth.atlassian.com/authorize`
   - **Token URL**: `https://auth.atlassian.com/oauth/token`
   - **Redirect URI**: `http://localhost:8080/callback` (for development)

4. **Add Scopes**
   - `read:jira-work`
   - `write:jira-work`
   - `read:jira-user`
   - `manage:jira-project`

5. **Get Credentials**
   - Copy the **Client ID**
   - Copy the **Client Secret**

### Step 2: Update Environment Variables
```bash
# Add to your .env file
JIRA_OAUTH_CLIENT_ID=your_client_id_here
JIRA_OAUTH_CLIENT_SECRET=your_client_secret_here
JIRA_OAUTH_REDIRECT_URI=http://localhost:8080/callback
```

### Step 3: OAuth Flow Implementation
The MCP server would need to handle the OAuth flow, which requires:
- Authorization code flow
- Token refresh handling
- State management

## Option 2: Direct API Integration (Recommended)

Since OAuth setup is complex, let's use the **Direct Jira API** approach:

### Benefits of Direct API:
- ✅ No OAuth complexity
- ✅ Works with API tokens
- ✅ Full control over operations
- ✅ Easier to implement and debug

### Implementation:
```python
# Direct Jira API client
class DirectJiraClient:
    def __init__(self, jira_url, api_token, email):
        self.jira_url = jira_url
        self.api_token = api_token
        self.email = email
        self.headers = {
            "Authorization": f"Basic {base64.b64encode(f'{email}:{api_token}'.encode()).decode()}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def create_issue(self, project_key, summary, description, issue_type="Incident"):
        # Direct API call implementation
        pass
    
    def search_issues(self, jql):
        # Direct API call implementation
        pass
```

## Option 3: Hybrid Approach (Current Implementation)

We already have a hybrid approach in our LangGraph system:
- **GitHub**: MCP integration (working)
- **Jira**: Direct API integration (after token fix)

### Current Status:
- ✅ **GitHub MCP**: Working with GitHub Copilot MCP
- ❌ **Jira MCP**: Requires OAuth setup
- 🔧 **Jira Direct API**: Ready (needs correct token)

## Recommended Next Steps

### Immediate (Recommended):
1. **Fix Jira API Token** (simpler than OAuth)
   - Get proper Atlassian API token
   - Test with direct API
   - Use hybrid approach

### Future (If needed):
1. **Set up OAuth** for full MCP integration
2. **Deploy OAuth flow** for production use
3. **Migrate to full MCP** when ready

## Quick Test Commands

```bash
# Test current token (after fixing)
python3 test_jira_token_validation.py

# Test hybrid approach
python3 test_hybrid_integration.py

# Test standalone MCP (after OAuth setup)
python3 test_jira_mcp_standalone.py
```

## Current Recommendation

**Use the Direct API approach** because:
1. ✅ Simpler to implement
2. ✅ No OAuth complexity
3. ✅ Works with API tokens
4. ✅ Full control over Jira operations
5. ✅ Can be upgraded to MCP later

The hybrid approach (GitHub MCP + Jira Direct API) gives you the best of both worlds without the OAuth complexity.
