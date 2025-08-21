# 🚀 Quick MCP Setup Guide

This guide helps you quickly set up external MCP server connections.

## 🔑 **Step 1: Get GitHub Token**

### **Create GitHub Personal Access Token**

1. **Visit GitHub Settings:**
   - Go to [GitHub Settings](https://github.com/settings)
   - Click "Developer settings" in left sidebar
   - Click "Personal access tokens" → "Fine-grained tokens"

2. **Generate New Token:**
   ```
   Token name: LangGraph Incident Response
   Expiration: 90 days
   
   Repository access: 
   - Select "Only select repositories"
   - Choose repositories to analyze
   
   Permissions:
   - Contents: Read-only
   - Metadata: Read-only
   - Pull requests: Read-only
   - Issues: Read-only
   ```

3. **Copy Token:**
   - Click "Generate token"
   - Copy the token (starts with `ghp_`)
   - Add to your `.env` file:
   ```bash
   GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
   ```

## 🌐 **Step 2: Get MCP_GITHUB_SERVER_URL**

### **Option A: Test with Local MCP Server (Quick Start)**

If you have Node.js installed:

```bash
# Install GitHub MCP server
npm install -g @modelcontextprotocol/server-github

# Run local server (replace with your details)
npx @modelcontextprotocol/server-github \
  --token YOUR_GITHUB_TOKEN \
  --owner YOUR_GITHUB_USERNAME \
  --repo YOUR_REPOSITORY_NAME

# Use local URL
MCP_GITHUB_SERVER_URL=http://localhost:3000
```

### **Option B: Use Public MCP Server**

Try these public MCP server URLs:

```bash
# Option 1: GitHub's official (if available)
MCP_GITHUB_SERVER_URL=https://api.github.com/mcp

# Option 2: Community server (example)
MCP_GITHUB_SERVER_URL=https://mcp.example.com/github

# Option C: Deploy to cloud
MCP_GITHUB_SERVER_URL=https://your-deployed-server.com
```

### **Option C: Deploy to Cloud Platform**

#### **Deploy to Railway (Free Tier)**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway init

# Deploy GitHub MCP server
railway up
```

#### **Deploy to Render (Free Tier)**

```bash
# Create render.yaml
services:
  - type: web
    name: github-mcp-server
    env: docker
    plan: free
    dockerfilePath: ./Dockerfile
    envVars:
      - key: GITHUB_PERSONAL_ACCESS_TOKEN
        value: your_token_here
```

## 🔧 **Step 3: Complete Configuration**

### **Update .env File**

```bash
# Copy environment template
cp env.example .env

# Edit with your values
nano .env
```

Add these lines to your `.env`:

```bash
# GitHub Configuration
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_actual_token_here
MCP_GITHUB_SERVER_URL=https://your-mcp-server-url.com

# OpenAI (Required for LLM)
OPENAI_API_KEY=your_openai_api_key_here
```

### **Test Configuration**

```bash
# Test the connection
python test_langchain_mcp.py
```

## 🧪 **Step 4: Test with Sample Data**

If you don't have external MCP servers yet, you can test with simulated data:

```bash
# Run without external MCP servers
python -m src.main
```

The system will use simulated data and show you what the external MCP integration would look like.

## 🔍 **Troubleshooting**

### **Token Issues**

```bash
# Test GitHub token
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user

# Expected response: {"login": "your_username", ...}
```

### **MCP Server Issues**

```bash
# Test MCP server health
curl https://your-mcp-server-url.com/health

# Expected response: {"status": "healthy"}
```

### **Common Errors**

1. **"Token not found"**: Check `GITHUB_PERSONAL_ACCESS_TOKEN` in `.env`
2. **"Server not reachable"**: Check `MCP_GITHUB_SERVER_URL` and network connectivity
3. **"Authentication failed"**: Verify token permissions and expiration

## 📚 **Next Steps**

1. **Get GitHub token** (required)
2. **Find or deploy MCP server** (choose option above)
3. **Configure .env file**
4. **Test connection**
5. **Run incident response system**

## 🆘 **Need Help?**

- **GitHub Token Issues**: [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- **MCP Server Issues**: [GitHub MCP Server](https://github.com/github/github-mcp-server)
- **LangChain MCP Adapters**: [Documentation](https://github.com/langchain-ai/langchain-mcp-adapters)
