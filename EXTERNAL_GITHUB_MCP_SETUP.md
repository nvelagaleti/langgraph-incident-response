# 🌐 External GitHub MCP Server Setup Guide

This guide shows how to use GitHub's official MCP server as an external service with the LangGraph Incident Response System.

## 🎯 Overview

Based on the [GitHub MCP Server documentation](https://github.com/github/github-mcp-server), you can use GitHub's official MCP server without installing anything locally. This provides:

- **No Local Installation**: No need to install Go, Docker, or npm packages
- **Official Support**: GitHub's official MCP server with full feature support
- **Enterprise Features**: Support for GitHub Enterprise and advanced toolsets
- **Better Performance**: Optimized server infrastructure

## 🚀 **Setup Options**

### **Option 1: Use GitHub's Hosted MCP Server (If Available)**

GitHub may provide a hosted version of their MCP server. Configure your `.env` file:

```bash
# GitHub's Official MCP Server (Hosted)
MCP_GITHUB_SERVER_URL=https://api.github.com/mcp
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_personal_access_token_here
```

### **Option 2: Use Docker-Based External Server**

Deploy the GitHub MCP server to a cloud platform:

```bash
# Deploy to cloud platform (AWS, GCP, Azure)
docker run -d \
  --name github-mcp-server \
  -p 3000:3000 \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token \
  -e GITHUB_TOOLSETS="repos,issues,pull_requests,actions,code_security" \
  ghcr.io/github/github-mcp-server
```

Then configure your `.env` file:

```bash
# External GitHub MCP Server (Docker)
MCP_GITHUB_SERVER_URL=http://your-server-ip:3000
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_personal_access_token_here
```

### **Option 3: Use Cloud-Hosted MCP Service**

Many cloud providers offer MCP server hosting:

```bash
# Example: Cloud-hosted MCP service
MCP_GITHUB_SERVER_URL=https://mcp.your-cloud-provider.com/github
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_personal_access_token_here
```

## 🔧 **Configuration**

### **Environment Variables**

Update your `.env` file:

```bash
# External GitHub MCP Server Configuration
MCP_GITHUB_SERVER_URL=https://your-mcp-server-url.com
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_personal_access_token_here

# Optional: GitHub Enterprise
GITHUB_HOST=https://your-ghe-instance.com

# OpenAI (Required for LLM)
OPENAI_API_KEY=your_openai_api_key_here
```

### **GitHub Token Setup**

1. **Create GitHub Personal Access Token:**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with required permissions:
     - `repo` (for repository access)
     - `read:org` (for organization repositories)
     - `read:user` (for user information)

2. **Fine-Grained Token (Recommended):**
   - Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Select specific repositories and permissions
   - Set expiration date for security

## 🛠️ **Available Features**

The GitHub MCP server provides extensive functionality:

### **Repository Management**
- List repositories
- Get repository details
- Search repositories
- Get repository contents

### **Commit Analysis**
- Get commits with filtering
- Get commit details
- Get file changes
- Search commits

### **Issue Tracking**
- List issues
- Create issues
- Update issues
- Add comments

### **Pull Request Management**
- List pull requests
- Create pull requests
- Review pull requests
- Merge pull requests

### **GitHub Actions**
- List workflows
- Get workflow runs
- Trigger workflows
- Get job logs

### **Security Features**
- Secret scanning alerts
- Code scanning alerts
- Dependency alerts
- Security advisories

## 🚀 **Quick Start**

### **Step 1: Configure Environment**

```bash
# Copy environment template
cp env.example .env

# Edit with your configuration
nano .env
```

### **Step 2: Test External Connection**

```bash
# Test external GitHub MCP server
python test_external_github_mcp.py
```

### **Step 3: Run Incident Response System**

```bash
# Run the full system with external MCP
python -m src.main
```

## 📊 **Multi-Repository Support**

The external GitHub MCP server supports multiple repositories:

### **Configuration**

```bash
# Multiple repositories (comma-separated)
GITHUB_REPOSITORIES=owner1/repo1,owner2/repo2,owner3/repo3
```

### **Usage**

The system will automatically:
- Connect to all configured repositories
- Analyze commits across repositories
- Correlate changes between services
- Generate comprehensive incident reports

## 🔒 **Security Considerations**

### **Token Security**

1. **Use Fine-Grained Tokens:**
   - Limit token scope to required repositories
   - Set appropriate expiration dates
   - Use organization-level tokens when possible

2. **Environment Security:**
   - Store tokens in secure environment variables
   - Use cloud secrets management
   - Never commit tokens to version control

3. **Network Security:**
   - Use HTTPS for external server connections
   - Implement proper firewall rules
   - Use VPN for internal deployments

### **Read-Only Mode**

For enhanced security, use read-only mode:

```bash
# Configure external server for read-only access
GITHUB_READ_ONLY=1
```

## 📈 **Performance Optimization**

### **Rate Limiting**

The GitHub MCP server respects GitHub's API rate limits:

- **Authenticated requests**: 5,000 requests per hour
- **Unauthenticated requests**: 60 requests per hour
- **Enterprise accounts**: Higher limits available

### **Caching**

The external server may provide caching for:
- Repository metadata
- Commit history
- Issue and PR data

### **Parallel Processing**

The system can process multiple repositories in parallel:
- Concurrent repository analysis
- Parallel commit retrieval
- Efficient cross-repository correlation

## 🛠️ **Troubleshooting**

### **Common Issues**

1. **Connection Failed:**
   ```bash
   # Check server URL
   curl -I https://your-mcp-server-url.com/health
   
   # Verify token permissions
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
   ```

2. **Authentication Errors:**
   ```bash
   # Check token scope
   # Ensure token has required permissions
   # Verify token hasn't expired
   ```

3. **Rate Limiting:**
   ```bash
   # Check rate limit status
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
   
   # Consider using GitHub Enterprise for higher limits
   ```

### **Debug Mode**

Enable debug mode for detailed logging:

```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

## 📚 **Advanced Configuration**

### **GitHub Enterprise**

For GitHub Enterprise Server or Enterprise Cloud:

```bash
# GitHub Enterprise Server
GITHUB_HOST=https://your-ghe-instance.com

# GitHub Enterprise Cloud with data residency
GITHUB_HOST=https://your-subdomain.ghe.com
```

### **Custom Toolsets**

Configure specific toolsets for your needs:

```bash
# Minimal toolsets for incident response
GITHUB_TOOLSETS=repos,issues,pull_requests

# Full feature set
GITHUB_TOOLSETS=all
```

### **Dynamic Tool Discovery**

Enable dynamic toolset discovery for better performance:

```bash
# Enable dynamic toolsets
GITHUB_DYNAMIC_TOOLSETS=1
```

## 🎯 **Use Cases**

### **Incident Response**

```bash
# Analyze recent changes across repositories
# Correlate commits with incidents
# Track issue and PR status
# Monitor security alerts
```

### **Change Management**

```bash
# Track deployment changes
# Monitor configuration updates
# Analyze dependency changes
# Review security updates
```

### **Compliance and Auditing**

```bash
# Audit repository access
# Track code changes
# Monitor security alerts
# Generate compliance reports
```

## 📚 **Additional Resources**

- [GitHub MCP Server Documentation](https://github.com/github/github-mcp-server)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub Enterprise Documentation](https://docs.github.com/en/enterprise)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)

## 🚀 **Next Steps**

1. **Configure your external GitHub MCP server**
2. **Test the connection with `test_external_github_mcp.py`**
3. **Run the full incident response system**
4. **Monitor and optimize performance**
5. **Implement security best practices**

The external GitHub MCP server provides a powerful, scalable solution for GitHub integration without requiring local installation or maintenance!
