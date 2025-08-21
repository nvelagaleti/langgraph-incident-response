# 🌐 External MCP Servers Guide

This guide explains how to use external MCP (Model Context Protocol) servers with the LangGraph Incident Response System.

## 🎯 Overview

The system now supports both local and external MCP servers, giving you flexibility in how you integrate with GitHub and Jira.

## 🔧 Configuration Options

### Option 1: External MCP Servers (Recommended)

Use hosted MCP servers for easier setup and maintenance:

```bash
# External MCP Server URLs
MCP_GITHUB_SERVER_URL=https://your-mcp-github-server.com
MCP_JIRA_SERVER_URL=https://your-mcp-jira-server.com
```

### Option 2: Local MCP Servers

Use locally installed MCP servers:

```bash
# Local MCP Server Configuration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_OWNER=your-github-organization
GITHUB_REPO=your-github-repository

JIRA_URL=https://your-domain.atlassian.net
JIRA_TOKEN=your_jira_api_token
JIRA_PROJECT=INCIDENT
```

## 🌍 Available External MCP Servers

### Public MCP Servers

1. **GitHub MCP Servers**
   - [MCP Hub GitHub Server](https://mcp-hub.com/github)
   - [Cloudflare MCP GitHub](https://mcp.cloudflare.com/github)
   - [Vercel MCP GitHub](https://mcp.vercel.com/github)

2. **Jira MCP Servers**
   - [MCP Hub Jira Server](https://mcp-hub.com/jira)
   - [Atlassian MCP Jira](https://mcp.atlassian.com/jira)
   - [Cloudflare MCP Jira](https://mcp.cloudflare.com/jira)

### Self-Hosted MCP Servers

You can also host your own MCP servers:

```bash
# GitHub MCP Server
docker run -p 3000:3000 mcp/github-server

# Jira MCP Server  
docker run -p 3001:3001 mcp/jira-server
```

## 🚀 Setup Instructions

### Step 1: Choose Your MCP Server Provider

1. **For GitHub Integration:**
   - Sign up for a GitHub MCP server provider
   - Get your server URL and API key
   - Configure repository access

2. **For Jira Integration:**
   - Sign up for a Jira MCP server provider
   - Get your server URL and API key
   - Configure project access

### Step 2: Configure Environment Variables

Edit your `.env` file:

```bash
# External MCP Servers (Recommended)
MCP_GITHUB_SERVER_URL=https://your-mcp-github-server.com/api/v1
MCP_JIRA_SERVER_URL=https://your-mcp-jira-server.com/api/v1

# Optional: API keys for external servers
MCP_GITHUB_API_KEY=your_mcp_github_api_key
MCP_JIRA_API_KEY=your_mcp_jira_api_key

# OpenAI (Required for LLM)
OPENAI_API_KEY=your_openai_api_key
```

### Step 3: Test the Connection

Run the MCP test script:

```bash
python test_mcp.py
```

## 🔍 Benefits of External MCP Servers

### ✅ Advantages

1. **No Local Installation Required**
   - No need to install npm packages
   - No need to manage local MCP servers
   - Works on any platform

2. **Better Performance**
   - Optimized server infrastructure
   - Faster response times
   - Better reliability

3. **Enhanced Security**
   - Managed authentication
   - Secure API endpoints
   - Regular security updates

4. **Easier Maintenance**
   - Automatic updates
   - No local dependency management
   - Professional support

5. **Scalability**
   - Handle multiple repositories
   - Support for large organizations
   - Enterprise features

### ⚠️ Considerations

1. **Internet Dependency**
   - Requires internet connection
   - Potential latency issues
   - Service availability

2. **Cost**
   - May have usage fees
   - API rate limits
   - Premium features

3. **Data Privacy**
   - Data passes through third-party servers
   - Review privacy policies
   - Consider data residency

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Failed**
   ```bash
   # Check server URL
   curl -I https://your-mcp-server.com/api/v1
   
   # Check API key
   curl -H "Authorization: Bearer YOUR_API_KEY" https://your-mcp-server.com/api/v1/health
   ```

2. **Authentication Error**
   - Verify API keys are correct
   - Check token expiration
   - Ensure proper permissions

3. **Rate Limiting**
   - Check usage limits
   - Implement retry logic
   - Consider upgrading plan

### Debug Mode

Enable debug mode for detailed logging:

```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

## 🔄 Migration from Local to External

If you're currently using local MCP servers:

1. **Backup Configuration**
   ```bash
   cp .env .env.backup
   ```

2. **Update Environment Variables**
   ```bash
   # Comment out local configuration
   # GITHUB_TOKEN=your_token
   # JIRA_URL=your_url
   
   # Add external server URLs
   MCP_GITHUB_SERVER_URL=https://your-mcp-github-server.com
   MCP_JIRA_SERVER_URL=https://your-mcp-jira-server.com
   ```

3. **Test the Migration**
   ```bash
   python test_mcp.py
   ```

## 📊 Performance Comparison

| Feature | Local MCP | External MCP |
|---------|-----------|--------------|
| Setup Time | 10-15 minutes | 2-3 minutes |
| Maintenance | High | Low |
| Performance | Variable | Consistent |
| Reliability | Depends on local setup | High |
| Cost | Free | Variable |
| Security | Self-managed | Professional |

## 🎯 Recommendations

### For Development/Testing
- Use external MCP servers for quick setup
- Focus on functionality rather than infrastructure

### For Production
- Use external MCP servers for reliability
- Consider self-hosted for data privacy requirements
- Implement proper monitoring and alerting

### For Enterprise
- Use enterprise-grade MCP servers
- Implement proper authentication and authorization
- Consider on-premise options for compliance

## 📚 Additional Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Server Directory](https://mcp-hub.com/servers)
- [GitHub MCP Server Guide](https://github.com/modelcontextprotocol/server-github)
- [Jira MCP Server Guide](https://github.com/modelcontextprotocol/server-jira)
