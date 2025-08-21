# 🐳 Docker-Based GitHub MCP Server Setup

This guide shows how to run GitHub's official MCP server using Docker for external access.

## 🚀 **Quick Setup with Docker**

### **Step 1: Run GitHub MCP Server with Docker**

```bash
# Run GitHub MCP server in Docker
docker run -d \
  --name github-mcp-server \
  -p 3000:3000 \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token \
  -e GITHUB_TOOLSETS="repos,issues,pull_requests,actions,code_security" \
  ghcr.io/github/github-mcp-server
```

### **Step 2: Configure LangGraph System**

Update your `.env` file:

```bash
# External GitHub MCP Server (Docker)
MCP_GITHUB_SERVER_URL=http://your-server-ip:3000
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_personal_access_token_here
```

## 🌐 **Cloud Deployment Options**

### **Option 1: Deploy to Cloud Platform**

#### **AWS EC2**
```bash
# Launch EC2 instance
# Install Docker
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Run GitHub MCP server
docker run -d \
  --name github-mcp-server \
  -p 80:3000 \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token \
  -e GITHUB_TOOLSETS="repos,issues,pull_requests" \
  ghcr.io/github/github-mcp-server
```

#### **Google Cloud Run**
```bash
# Deploy to Cloud Run
gcloud run deploy github-mcp-server \
  --image ghcr.io/github/github-mcp-server \
  --platform managed \
  --allow-unauthenticated \
  --port 3000 \
  --set-env-vars GITHUB_PERSONAL_ACCESS_TOKEN=your_token,GITHUB_TOOLSETS=repos,issues,pull_requests
```

#### **Azure Container Instances**
```bash
# Deploy to Azure Container Instances
az container create \
  --resource-group myResourceGroup \
  --name github-mcp-server \
  --image ghcr.io/github/github-mcp-server \
  --ports 3000 \
  --environment-variables GITHUB_PERSONAL_ACCESS_TOKEN=your_token GITHUB_TOOLSETS=repos,issues,pull_requests
```

### **Option 2: Use Docker Compose**

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  github-mcp-server:
    image: ghcr.io/github/github-mcp-server
    ports:
      - "3000:3000"
    environment:
      - GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_PERSONAL_ACCESS_TOKEN}
      - GITHUB_TOOLSETS=repos,issues,pull_requests,actions,code_security
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

## 🔧 **Configuration Options**

### **Environment Variables**

```bash
# Required
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token

# Optional
GITHUB_TOOLSETS=repos,issues,pull_requests,actions,code_security
GITHUB_HOST=https://api.github.com
GITHUB_READ_ONLY=1
GITHUB_DYNAMIC_TOOLSETS=1
```

### **Available Toolsets**

The GitHub MCP server supports these toolsets:

- **repos**: Repository management
- **issues**: Issue tracking
- **pull_requests**: Pull request management
- **actions**: GitHub Actions
- **code_security**: Security scanning
- **experiments**: Experimental features
- **all**: All toolsets

### **Read-Only Mode**

For security, you can run in read-only mode:

```bash
docker run -d \
  --name github-mcp-server \
  -p 3000:3000 \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=your_token \
  -e GITHUB_READ_ONLY=1 \
  ghcr.io/github/github-mcp-server
```

## 🔒 **Security Considerations**

### **Token Management**

1. **Use Fine-Grained Tokens:**
   ```bash
   # Create token with minimal permissions
   # Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
   # Select only required repositories and permissions
   ```

2. **Environment Variable Security:**
   ```bash
   # Use secrets management
   # Don't hardcode tokens in docker-compose files
   # Use .env files or cloud secrets
   ```

3. **Network Security:**
   ```bash
   # Use HTTPS in production
   # Implement proper firewall rules
   # Use VPN for internal deployments
   ```

## 📊 **Monitoring and Health Checks**

### **Health Check Endpoint**

```bash
# Check if server is running
curl http://your-server:3000/health

# Expected response: {"status": "healthy"}
```

### **Logs and Monitoring**

```bash
# View logs
docker logs github-mcp-server

# Monitor resource usage
docker stats github-mcp-server

# Set up monitoring
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  prom/prometheus
```

## 🚀 **Production Deployment**

### **High Availability Setup**

```yaml
version: '3.8'
services:
  github-mcp-server:
    image: ghcr.io/github/github-mcp-server
    ports:
      - "3000:3000"
    environment:
      - GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_TOKEN}
      - GITHUB_TOOLSETS=repos,issues,pull_requests
    restart: unless-stopped
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### **Load Balancer Configuration**

```bash
# Use nginx as load balancer
docker run -d \
  --name nginx-lb \
  -p 80:80 \
  -v /path/to/nginx.conf:/etc/nginx/nginx.conf \
  nginx:alpine
```

## 🔧 **Troubleshooting**

### **Common Issues**

1. **Connection Refused:**
   ```bash
   # Check if container is running
   docker ps
   
   # Check logs
   docker logs github-mcp-server
   
   # Verify port mapping
   docker port github-mcp-server
   ```

2. **Authentication Errors:**
   ```bash
   # Verify token permissions
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
   
   # Check token scope
   # Ensure token has required permissions
   ```

3. **Rate Limiting:**
   ```bash
   # Check rate limit status
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
   
   # Consider using GitHub Enterprise for higher limits
   ```

## 📚 **Additional Resources**

- [GitHub MCP Server Documentation](https://github.com/github/github-mcp-server)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub API Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
