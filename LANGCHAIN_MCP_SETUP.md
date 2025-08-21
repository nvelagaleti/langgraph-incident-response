# 🔌 LangChain MCP Adapters Setup Guide

This guide shows how to use [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters) to connect to external MCP servers without any local installation.

## 🎯 Overview

The [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters) library provides seamless integration with external MCP servers using **streamable HTTP transport**. This means you can connect to external MCP servers using just URLs - no local installation required!

### ✅ **Key Benefits**

- **No Local Installation**: Connect to external MCP servers via URLs
- **Streamable HTTP Transport**: Modern HTTP-based MCP communication
- **Multi-Server Support**: Connect to multiple MCP servers simultaneously
- **LangGraph Integration**: Native integration with LangGraph workflows
- **Authentication Support**: Built-in support for headers and tokens
- **Error Handling**: Robust error handling and fallback mechanisms

## 🚀 **Quick Start**

### **Step 1: Install Dependencies**

```bash
# Install LangChain MCP Adapters
pip install langchain-mcp-adapters>=0.1.9

# Or update requirements.txt
echo "langchain-mcp-adapters>=0.1.9" >> requirements.txt
pip install -r requirements.txt
```

### **Step 2: Configure Environment**

```bash
# Copy environment template
cp env.example .env

# Edit with your external MCP server URLs
nano .env
```

### **Step 3: Set External MCP Server URLs**

```bash
# External GitHub MCP Server
MCP_GITHUB_SERVER_URL=https://your-github-mcp-server.com
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token

# External Jira MCP Server
MCP_JIRA_SERVER_URL=https://your-jira-mcp-server.com
JIRA_TOKEN=your_jira_token
```

### **Step 4: Test Connection**

```bash
# Test LangChain MCP client
python test_langchain_mcp.py
```

### **Step 5: Run Incident Response System**

```bash
# Run with external MCP servers
python -m src.main
```

## 🔧 **Configuration Options**

### **External MCP Server Configuration**

The LangChain MCP Adapters support multiple external server configurations:

#### **Option 1: GitHub's Official MCP Server**

```bash
# If GitHub provides a hosted MCP server
MCP_GITHUB_SERVER_URL=https://api.github.com/mcp
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token
```

#### **Option 2: Custom External MCP Servers**

```bash
# Custom GitHub MCP server
MCP_GITHUB_SERVER_URL=https://your-github-mcp-server.com
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token

# Custom Jira MCP server
MCP_JIRA_SERVER_URL=https://your-jira-mcp-server.com
JIRA_TOKEN=your_jira_token
```

#### **Option 3: Docker-Based External Servers**

```bash
# Docker-based GitHub MCP server
MCP_GITHUB_SERVER_URL=http://your-server-ip:3000
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token

# Docker-based Jira MCP server
MCP_JIRA_SERVER_URL=http://your-server-ip:3001
JIRA_TOKEN=your_jira_token
```

### **Authentication Headers**

The LangChain MCP Adapters automatically handle authentication headers:

```python
# Headers are automatically added based on environment variables
servers_config = {
    "github": {
        "transport": "streamable_http",
        "url": "https://your-github-mcp-server.com",
        "headers": {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json"
        }
    }
}
```

## 🛠️ **Available Features**

### **GitHub MCP Server Features**

The LangChain MCP Adapters support all GitHub MCP server features:

#### **Repository Management**
- List repositories
- Get repository details
- Search repositories
- Get repository contents

#### **Commit Analysis**
- Get commits with filtering
- Get commit details
- Get file changes
- Search commits

#### **Issue Tracking**
- List issues
- Create issues
- Update issues
- Add comments

#### **Pull Request Management**
- List pull requests
- Create pull requests
- Review pull requests
- Merge pull requests

#### **GitHub Actions**
- List workflows
- Get workflow runs
- Trigger workflows
- Get job logs

#### **Security Features**
- Secret scanning alerts
- Code scanning alerts
- Dependency alerts
- Security advisories

### **Jira MCP Server Features**

#### **Issue Management**
- Create issues
- Update issues
- Search issues
- Add comments

#### **Project Management**
- List projects
- Get project details
- Create projects

#### **Workflow Management**
- List workflows
- Transition issues
- Get workflow status

## 📊 **Multi-Server Support**

The LangChain MCP Adapters support connecting to multiple MCP servers simultaneously:

```python
# Multiple server configuration
servers_config = {
    "github": {
        "transport": "streamable_http",
        "url": "https://github-mcp-server.com",
        "headers": {"Authorization": f"Bearer {github_token}"}
    },
    "jira": {
        "transport": "streamable_http",
        "url": "https://jira-mcp-server.com",
        "headers": {"Authorization": f"Bearer {jira_token}"}
    },
    "custom": {
        "transport": "streamable_http",
        "url": "https://custom-mcp-server.com",
        "headers": {"X-API-Key": "your_api_key"}
    }
}
```

## 🔒 **Security Features**

### **Authentication**

The LangChain MCP Adapters support various authentication methods:

#### **Bearer Token Authentication**
```bash
# GitHub Personal Access Token
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here

# Jira API Token
JIRA_TOKEN=your_jira_token_here
```

#### **Custom Headers**
```python
# Custom authentication headers
headers = {
    "Authorization": "Bearer your_token",
    "X-API-Key": "your_api_key",
    "X-Custom-Header": "custom_value"
}
```

### **HTTPS Support**

All external MCP server connections use HTTPS for security:

```bash
# Secure connections
MCP_GITHUB_SERVER_URL=https://your-github-mcp-server.com
MCP_JIRA_SERVER_URL=https://your-jira-mcp-server.com
```

### **Token Management**

#### **Fine-Grained GitHub Tokens**
```bash
# Create fine-grained token with minimal permissions
# Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
# Select only required repositories and permissions
```

#### **Jira API Tokens**
```bash
# Create Jira API token with appropriate permissions
# Go to Atlassian Account Settings → Security → Create API token
```

## 📈 **Performance Optimization**

### **Connection Pooling**

The LangChain MCP Adapters use efficient connection pooling:

```python
# Automatic connection management
client = MultiServerMCPClient(servers_config)
tools = await client.get_tools()  # Efficient tool loading
```

### **Caching**

External MCP servers may provide caching for:
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

#### **1. Connection Failed**
```bash
# Check server URL
curl -I https://your-mcp-server-url.com/health

# Verify token permissions
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

#### **2. Authentication Errors**
```bash
# Check token scope and permissions
# Ensure token hasn't expired
# Verify token format
```

#### **3. Tool Loading Issues**
```bash
# Check server health
curl https://your-mcp-server-url.com/health

# Verify server supports required tools
# Check server logs for errors
```

### **Debug Mode**

Enable debug mode for detailed logging:

```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

### **Health Checks**

Test external server connectivity:

```bash
# Test GitHub MCP server
curl https://your-github-mcp-server.com/health

# Test Jira MCP server
curl https://your-jira-mcp-server.com/health
```

## 📚 **Advanced Configuration**

### **Custom Headers**

Add custom headers for authentication or tracing:

```python
servers_config = {
    "github": {
        "transport": "streamable_http",
        "url": "https://github-mcp-server.com",
        "headers": {
            "Authorization": f"Bearer {github_token}",
            "X-Trace-ID": "your_trace_id",
            "X-Custom-Header": "custom_value"
        }
    }
}
```

### **Timeout Configuration**

Configure connection timeouts:

```python
# Timeout configuration (if supported by the adapter)
servers_config = {
    "github": {
        "transport": "streamable_http",
        "url": "https://github-mcp-server.com",
        "timeout": 30  # 30 seconds timeout
    }
}
```

### **Retry Logic**

The LangChain MCP Adapters include built-in retry logic for:
- Network failures
- Temporary server errors
- Rate limiting

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

- [LangChain MCP Adapters Documentation](https://github.com/langchain-ai/langchain-mcp-adapters)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [GitHub MCP Server](https://github.com/github/github-mcp-server)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)

## 🚀 **Next Steps**

1. **Configure your external MCP server URLs**
2. **Set up your GitHub and Jira tokens**
3. **Test the connection with `test_langchain_mcp.py`**
4. **Run the full incident response system**
5. **Monitor and optimize performance**
6. **Implement security best practices**

The LangChain MCP Adapters provide a powerful, scalable solution for external MCP server integration without requiring any local installation or maintenance!
