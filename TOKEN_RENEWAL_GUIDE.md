# Jira OAuth Token Renewal System

A comprehensive solution for managing OAuth token lifecycle, including automatic renewal, expiry monitoring, and seamless integration with MCP clients.

## 🎯 Overview

This system provides:
- ✅ **Automatic token renewal** before expiry
- ✅ **Background monitoring** of token status
- ✅ **Seamless MCP integration** with token management
- ✅ **Manual and automatic renewal** options
- ✅ **Token validation and testing** tools

## 📁 Components

### Core Files
- `token_manager.py` - Main token management system
- `mcp_client_with_token_manager.py` - Enhanced MCP client with token management
- `jira_oauth_simple.py` - OAuth flow for token generation
- `exchange_token.py` - Token exchange utility

## 🚀 Quick Start

### 1. Check Token Status

```bash
python3 token_manager.py status
```

### 2. Manually Renew Token

```bash
python3 token_manager.py renew
```

### 3. Start Auto-Monitoring

```bash
python3 token_manager.py monitor
```

### 4. Test Current Token

```bash
python3 token_manager.py test
```

## 🔧 Token Manager Features

### Automatic Renewal
The token manager automatically:
- Monitors token expiry (5-minute buffer)
- Initiates OAuth flow when needed
- Updates environment variables and .env file
- Provides seamless token access

### Background Monitoring
```python
from token_manager import TokenManager

# Initialize token manager
token_manager = TokenManager()

# Start automatic monitoring
token_manager.start_auto_renewal()

# Stop monitoring when done
token_manager.stop_auto_renewal()
```

### Manual Token Management
```python
# Check if token is valid
if token_manager.is_token_valid():
    token = token_manager.get_valid_token()
    print(f"Token: {token}")

# Ensure valid token (renews if needed)
token = await token_manager.ensure_valid_token()
```

## 🔗 MCP Integration

### Enhanced MCP Client
```python
from mcp_client_with_token_manager import MCPClientWithTokenManager

# Initialize with automatic token management
client = MCPClientWithTokenManager()
await client.initialize()

# Use tools with automatic token renewal
tools = await client.get_tools()
result = await client.invoke_tool('get_projects', {})

# Close when done
await client.close()
```

### Wrapper for Existing Scripts
```python
from mcp_client_with_token_manager import TokenAwareMCPWrapper

# Wrap existing script with token management
wrapper = TokenAwareMCPWrapper('test_official_jira_mcp.py')
await wrapper.run_with_token_management()
```

## 📊 Token Status Information

### Status Output Example
```
🔍 Token Status
==================================================
✅ Has Access Token: True
🔄 Has Refresh Token: False
⚙️  Auto-renewal Enabled: True
🔄 Auto-renewal Running: False
📋 Token Type: Bearer

⏰ Expiry Information:
   Valid: True
   Expires At: 2025-08-20T15:59:35
   Time Until Expiry: 0:45:23
   Needs Renewal: False
```

### Programmatic Status Check
```python
status = token_manager.get_token_status()
print(f"Token valid: {status['expiry_info']['valid']}")
print(f"Expires at: {status['expiry_info']['expires_at']}")
print(f"Needs renewal: {status['expiry_info']['needs_renewal']}")
```

## 🔄 Renewal Strategies

### 1. Automatic Background Renewal
```python
# Start monitoring in background
token_manager.start_auto_renewal()

# Your application continues running
# Token will be automatically renewed when needed
```

### 2. On-Demand Renewal
```python
# Check and renew when needed
if not token_manager.is_token_valid():
    await token_manager.renew_token_oauth_flow()
```

### 3. Proactive Renewal
```python
# Always ensure valid token before operations
token = await token_manager.ensure_valid_token()
if token:
    # Use token for API calls
    pass
```

## 🛠️ Configuration

### Environment Variables
```bash
# Required
JIRA_OAUTH_CLIENT_ID=IRpTkSYRqY2sPc2FxhHOJGpib4klKpXP
JIRA_OAUTH_CLIENT_SECRET=your_client_secret_here

# Optional (with defaults)
JIRA_OAUTH_REDIRECT_URI=http://localhost:8080/callback
JIRA_OAUTH_ACCESS_TOKEN=auto_generated
JIRA_OAUTH_REFRESH_TOKEN=auto_generated
```

### Renewal Settings
```python
# Configure renewal buffer (default: 5 minutes)
token_manager.renewal_buffer_minutes = 10

# Enable/disable auto-renewal
token_manager.auto_renewal_enabled = True
```

## 🔒 Security Considerations

### Token Storage
- ✅ Tokens stored in environment variables
- ✅ Automatic .env file updates
- ✅ No hardcoded tokens in code
- ✅ Secure token handling

### Token Lifecycle
- ⏰ Access tokens expire in 1 hour
- 🔄 Automatic renewal before expiry
- 🛡️ Secure OAuth flow for renewal
- 📝 Comprehensive logging and monitoring

## 🧪 Testing and Validation

### Token Testing
```bash
# Test current token
python3 token_manager.py test
```

### MCP Integration Testing
```bash
# Test enhanced MCP client
python3 mcp_client_with_token_manager.py
```

### Manual Validation
```python
# Test token with API call
import requests

token = token_manager.get_valid_token()
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.atlassian.com/oauth/token/accessible-resources", headers=headers)
print(f"Status: {response.status_code}")
```

## 🔄 Integration with Existing Code

### Update Existing Scripts
```python
# Before (manual token handling)
from dotenv import load_dotenv
import os
load_dotenv()
token = os.getenv("JIRA_OAUTH_ACCESS_TOKEN")

# After (automatic token management)
from token_manager import TokenManager
token_manager = TokenManager()
token = await token_manager.ensure_valid_token()
```

### MCP Client Integration
```python
# Before (basic MCP client)
from langchain_mcp_adapters.client import MultiServerMCPClient
client = MultiServerMCPClient(servers_config)

# After (enhanced with token management)
from mcp_client_with_token_manager import MCPClientWithTokenManager
client = MCPClientWithTokenManager()
await client.initialize()
```

## 🚨 Troubleshooting

### Common Issues

1. **Token Expiry**
   ```bash
   # Check token status
   python3 token_manager.py status
   
   # Manually renew if needed
   python3 token_manager.py renew
   ```

2. **OAuth Flow Issues**
   - Ensure client secret is configured
   - Check redirect URI matches OAuth app settings
   - Verify browser can access authorization URL

3. **MCP Connection Issues**
   - Test token validity first
   - Check MCP server URL
   - Verify network connectivity

4. **Auto-Renewal Not Working**
   - Check if monitoring is running
   - Verify renewal buffer settings
   - Check for error logs

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug output for token manager
token_manager = TokenManager()
```

## 📈 Best Practices

### Production Deployment
1. **Use auto-renewal** for long-running applications
2. **Monitor token status** regularly
3. **Handle renewal failures** gracefully
4. **Log token operations** for debugging
5. **Secure token storage** in production environments

### Development Workflow
1. **Test token renewal** before deployment
2. **Use manual renewal** for development
3. **Monitor token expiry** during testing
4. **Validate MCP integration** with token management

### Error Handling
```python
try:
    token = await token_manager.ensure_valid_token()
    if not token:
        # Handle token renewal failure
        print("Failed to obtain valid token")
        return
except Exception as e:
    # Handle unexpected errors
    print(f"Token management error: {e}")
```

## 🎉 Success Metrics

With this token renewal system, you should see:
- ✅ **Zero token expiry errors** in production
- ✅ **Seamless MCP operations** without manual intervention
- ✅ **Automatic token renewal** before expiry
- ✅ **Comprehensive monitoring** and logging
- ✅ **Easy integration** with existing code

## 📚 Additional Resources

- [OAuth Setup Guide](JIRA_OAUTH_QUICK_SETUP.md)
- [Complete OAuth Documentation](README_OAUTH_COMPLETE.md)
- [MCP Integration Guide](LANGCHAIN_MCP_SETUP.md)
- [Atlassian OAuth Documentation](https://developer.atlassian.com/cloud/jira/platform/oauth-2-authorization-code-grants-3lo-for-apps/)

Your Jira OAuth token renewal system is now ready for production use! 🚀
