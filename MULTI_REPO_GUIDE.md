# 🔗 Multi-Repository GitHub MCP Support

This guide explains how to use the LangGraph Incident Response System with multiple GitHub repositories using local MCP servers.

## 🎯 Overview

The system now supports analyzing multiple GitHub repositories simultaneously, allowing you to:
- Track commits across multiple repositories
- Correlate changes between different services
- Perform comprehensive incident analysis across your entire codebase

## 🔧 Configuration Options

### Option 1: Multiple Repositories (Recommended)

Configure multiple repositories in your `.env` file:

```bash
# GitHub MCP Configuration for Multiple Repositories
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_REPOSITORIES=owner1/repo1,owner2/repo2,owner3/repo3
```

### Option 2: Single Repository (Legacy)

For backward compatibility, you can still use a single repository:

```bash
# Single Repository Configuration
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_OWNER=your-github-organization
GITHUB_REPO=your-github-repository
```

## 🚀 Setup Instructions

### Step 1: Install Local MCP Server

```bash
# Install the GitHub MCP server globally
npm install -g @modelcontextprotocol/server-github
```

### Step 2: Configure GitHub Token

1. **Create GitHub Personal Access Token:**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `repo` permissions
   - Copy the token

2. **Set Environment Variables:**
   ```bash
   # Edit your .env file
   GITHUB_TOKEN=ghp_your_github_token_here
   ```

### Step 3: Configure Multiple Repositories

Add your repositories to the `.env` file:

```bash
# Example: Multiple repositories
GITHUB_REPOSITORIES=myorg/backend-service,myorg/frontend-app,myorg/api-gateway

# Example: Different organizations
GITHUB_REPOSITORIES=company/backend,team/frontend,devops/infrastructure
```

### Step 4: Test Multi-Repo Setup

```bash
# Test the configuration
python test_mcp.py
```

## 📊 How Multi-Repo Analysis Works

### Repository Session Management

The system creates separate MCP sessions for each repository:

```python
# Each repository gets its own MCP session
repo1_session = await mcp_client.get_repo_session("owner1", "repo1")
repo2_session = await mcp_client.get_repo_session("owner2", "repo2")
repo3_session = await mcp_client.get_repo_session("owner3", "repo3")
```

### Commit Analysis Process

1. **Parallel Repository Analysis:**
   - Analyzes each repository independently
   - Collects commits from all repositories
   - Correlates changes across repositories

2. **Cross-Repository Correlation:**
   - Identifies related changes across repositories
   - Tracks dependencies between services
   - Analyzes impact across the entire system

3. **Comprehensive Reporting:**
   - Generates unified incident reports
   - Shows repository-specific findings
   - Provides cross-repository insights

## 🔍 Use Cases

### 1. Microservices Architecture

```bash
# Analyze all microservices
GITHUB_REPOSITORIES=myorg/user-service,myorg/order-service,myorg/payment-service,myorg/notification-service
```

### 2. Frontend and Backend

```bash
# Analyze both frontend and backend
GITHUB_REPOSITORIES=myorg/backend-api,myorg/frontend-web,myorg/mobile-app
```

### 3. Infrastructure and Application

```bash
# Analyze application and infrastructure
GITHUB_REPOSITORIES=myorg/application,myorg/terraform-infra,myorg/kubernetes-configs
```

### 4. Multiple Teams

```bash
# Analyze repositories from different teams
GITHUB_REPOSITORIES=team-a/service1,team-b/service2,team-c/service3,devops/infrastructure
```

## 📈 Performance Considerations

### Session Management

- **Session Reuse:** Sessions are cached and reused for efficiency
- **Lazy Loading:** Sessions are created only when needed
- **Connection Pooling:** Multiple sessions can run simultaneously

### Rate Limiting

- **GitHub API Limits:** Respects GitHub's API rate limits
- **Parallel Processing:** Analyzes repositories in parallel when possible
- **Error Handling:** Gracefully handles rate limit errors

### Memory Usage

- **Session Cleanup:** Sessions are properly closed after use
- **Memory Optimization:** Efficient data structures for large commit histories
- **Resource Management:** Automatic cleanup of unused sessions

## 🛠️ Troubleshooting

### Common Issues

1. **Repository Access Denied**
   ```bash
   # Check token permissions
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user/repos
   
   # Ensure token has repo scope
   # Go to GitHub Settings → Developer settings → Personal access tokens
   ```

2. **Repository Not Found**
   ```bash
   # Verify repository names
   # Check for typos in GITHUB_REPOSITORIES
   # Ensure repositories exist and are accessible
   ```

3. **Rate Limiting**
   ```bash
   # Check rate limit status
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
   
   # Consider using GitHub Enterprise for higher limits
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
DEBUG_MODE=true
LOG_LEVEL=DEBUG
```

## 📊 Example Output

### Multi-Repo Analysis Results

```
🔍 Analyzing Git commits across repositories...
📊 Found 15 commits in myorg/backend-service
📊 Found 8 commits in myorg/frontend-app  
📊 Found 3 commits in myorg/api-gateway

📋 Cross-repository findings:
- Backend API changes in backend-service
- Frontend updates in frontend-app
- Gateway configuration in api-gateway

🎯 Root cause analysis:
- Configuration change in api-gateway caused backend timeout
- Frontend changes exposed the issue
- Backend service was not properly handling the timeout
```

## 🔄 Migration from Single to Multi-Repo

### Step 1: Backup Current Configuration

```bash
cp .env .env.backup
```

### Step 2: Update Configuration

```bash
# Old single repo configuration
# GITHUB_OWNER=myorg
# GITHUB_REPO=my-service

# New multi-repo configuration
GITHUB_REPOSITORIES=myorg/backend-service,myorg/frontend-app,myorg/api-gateway
```

### Step 3: Test Migration

```bash
python test_mcp.py
```

## 🎯 Best Practices

### Repository Organization

1. **Logical Grouping:**
   ```bash
   # Group related repositories
   GITHUB_REPOSITORIES=myorg/core-services,myorg/frontend-apps,myorg/infrastructure
   ```

2. **Team-Based Organization:**
   ```bash
   # Organize by team ownership
   GITHUB_REPOSITORIES=team-a/service1,team-b/service2,team-c/service3
   ```

3. **Service-Based Organization:**
   ```bash
   # Organize by service type
   GITHUB_REPOSITORIES=myorg/user-service,myorg/order-service,myorg/payment-service
   ```

### Token Management

1. **Scope Minimization:**
   - Use tokens with minimal required permissions
   - Regularly rotate tokens
   - Monitor token usage

2. **Organization Tokens:**
   - Consider using organization-level tokens
   - Use GitHub Apps for better security
   - Implement proper token rotation

### Performance Optimization

1. **Repository Selection:**
   - Only include relevant repositories
   - Exclude archived or inactive repositories
   - Consider repository size and activity

2. **Analysis Frequency:**
   - Adjust analysis time windows based on needs
   - Use appropriate commit history depth
   - Balance thoroughness with performance

## 📚 Additional Resources

- [GitHub MCP Server Documentation](https://github.com/modelcontextprotocol/server-github)
- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
