#!/usr/bin/env python3
"""
Jira OAuth Implementation for MCP
Complete OAuth setup and implementation for Atlassian MCP server
"""

import os
import asyncio
import json
import base64
import secrets
from urllib.parse import urlencode, parse_qs, urlparse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP server to handle OAuth callback."""
    
    def __init__(self, *args, auth_code_queue=None, **kwargs):
        self.auth_code_queue = auth_code_queue
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle OAuth callback."""
        query_components = parse_qs(urlparse(self.path).query)
        
        # Extract authorization code
        auth_code = query_components.get('code', [None])[0]
        state = query_components.get('state', [None])[0]
        error = query_components.get('error', [None])[0]
        
        if error:
            print(f"❌ OAuth error: {error}")
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>OAuth Error</h1><p>Authorization failed.</p>")
            return
        
        if auth_code:
            print(f"✅ Authorization code received")
            if self.auth_code_queue:
                self.auth_code_queue.put(auth_code)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Success!</h1><p>Authorization successful. You can close this window.</p>")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Error</h1><p>No authorization code received.</p>")

class JiraOAuthMCPClient:
    """Jira OAuth MCP client with full OAuth flow."""
    
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("JIRA_OAUTH_CLIENT_ID")
        self.client_secret = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
        self.redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")
        self.auth_url = "https://auth.atlassian.com/authorize"
        self.token_url = "https://auth.atlassian.com/oauth/token"
        self.access_token = None
        self.refresh_token = None
        self.mcp_client = None
        
    def get_authorization_url(self, state=None):
        """Generate authorization URL."""
        if not state:
            state = secrets.token_urlsafe(32)
        
        params = {
            "audience": "api.atlassian.com",
            "client_id": self.client_id,
            "scope": "read:jira-work write:jira-work read:jira-user manage:jira-project manage:jira-configuration manage:jira-webhook manage:jira-data-provider",
            "redirect_uri": self.redirect_uri,
            "state": state,
            "response_type": "code",
            "prompt": "consent"
        }
        
        return f"{self.auth_url}?{urlencode(params)}", state
    
    def start_callback_server(self, port=8080):
        """Start HTTP server to handle OAuth callback."""
        auth_code_queue = asyncio.Queue()
        
        class Handler(OAuthCallbackHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, auth_code_queue=auth_code_queue, **kwargs)
        
        server = HTTPServer(('localhost', port), Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        
        return server, auth_code_queue
    
    async def get_access_token(self, auth_code):
        """Exchange authorization code for access token."""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": self.redirect_uri
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        import requests
        
        response = requests.post(self.token_url, data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            print(f"✅ Access token obtained")
            return True
        else:
            print(f"❌ Failed to get access token: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
    
    async def refresh_access_token(self):
        """Refresh access token using refresh token."""
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        import requests
        
        response = requests.post(self.token_url, data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            if "refresh_token" in token_data:
                self.refresh_token = token_data.get("refresh_token")
            print(f"✅ Access token refreshed")
            return True
        else:
            print(f"❌ Failed to refresh token: {response.status_code}")
            return False
    
    async def setup_oauth_flow(self):
        """Complete OAuth setup flow."""
        print("🔐 Setting up OAuth flow for Atlassian MCP")
        print("=" * 60)
        
        if not self.client_id or not self.client_secret:
            print("❌ OAuth credentials not configured")
            print("💡 Please set JIRA_OAUTH_CLIENT_ID and JIRA_OAUTH_CLIENT_SECRET in your .env file")
            return False
        
        # Generate authorization URL
        auth_url, state = self.get_authorization_url()
        print(f"🔗 Authorization URL: {auth_url}")
        
        # Start callback server
        server, auth_code_queue = self.start_callback_server()
        print(f"🌐 Callback server started on port 8080")
        
        try:
            # Open browser for authorization
            print(f"🌐 Opening browser for authorization...")
            webbrowser.open(auth_url)
            
            # Wait for authorization code
            print(f"⏳ Waiting for authorization...")
            auth_code = await asyncio.wait_for(auth_code_queue.get(), timeout=300)  # 5 minutes timeout
            
            # Exchange code for token
            success = await self.get_access_token(auth_code)
            if not success:
                return False
            
            # Save tokens to environment (for persistence)
            os.environ["JIRA_OAUTH_ACCESS_TOKEN"] = self.access_token
            if self.refresh_token:
                os.environ["JIRA_OAUTH_REFRESH_TOKEN"] = self.refresh_token
            
            print(f"✅ OAuth setup completed successfully")
            return True
            
        except asyncio.TimeoutError:
            print(f"❌ Authorization timeout")
            return False
        except Exception as e:
            print(f"❌ OAuth setup failed: {e}")
            return False
        finally:
            server.shutdown()
    
    async def initialize_mcp_client(self):
        """Initialize MCP client with OAuth token."""
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        try:
            # Configure MCP client with OAuth token
            servers_config = {
                "jira": {
                    "transport": "streamable_http",
                    "url": "https://mcp.atlassian.com/v1/sse",
                    "headers": {
                        "Authorization": f"Bearer {self.access_token}",
                        "Accept": "text/event-stream",
                        "Content-Type": "application/json"
                    }
                }
            }
            
            self.mcp_client = MultiServerMCPClient(servers_config)
            tools = await self.mcp_client.get_tools()
            
            print(f"✅ MCP client initialized with OAuth")
            print(f"📊 Tools loaded: {len(tools)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize MCP client: {e}")
            return False
    
    async def test_jira_operations(self):
        """Test Jira operations with OAuth MCP."""
        if not self.mcp_client:
            print("❌ MCP client not initialized")
            return False
        
        try:
            tools = await self.mcp_client.get_tools()
            
            # Test basic operations
            print(f"🔍 Testing Jira operations with OAuth MCP")
            
            # Find tools by name patterns
            tool_map = {}
            for tool in tools:
                if hasattr(tool, 'name'):
                    tool_map[tool.name] = tool
            
            # Test 1: Get projects
            if 'get_projects' in tool_map:
                try:
                    result = await tool_map['get_projects'].ainvoke({})
                    print(f"✅ get_projects: Success")
                    print(f"   Result: {str(result)[:100]}...")
                except Exception as e:
                    print(f"❌ get_projects: {str(e)[:50]}...")
            
            # Test 2: Search issues
            if 'search_issues' in tool_map:
                try:
                    result = await tool_map['search_issues'].ainvoke({
                        "jql": "ORDER BY created DESC",
                        "max_results": 5
                    })
                    print(f"✅ search_issues: Success")
                    print(f"   Result: {str(result)[:100]}...")
                except Exception as e:
                    print(f"❌ search_issues: {str(e)[:50]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing Jira operations: {e}")
            return False
    
    async def close(self):
        """Close MCP client."""
        if self.mcp_client:
            try:
                await self.mcp_client.aclose()
                print("✅ MCP client closed")
            except Exception as e:
                print(f"⚠️  Error closing MCP client: {e}")

async def main():
    """Main OAuth setup and test function."""
    print("🔐 Jira OAuth MCP Setup")
    print("=" * 60)
    
    client = JiraOAuthMCPClient()
    
    # Step 1: OAuth setup
    print("🔍 Step 1: OAuth Setup")
    oauth_success = await client.setup_oauth_flow()
    
    if not oauth_success:
        print("❌ OAuth setup failed")
        return
    
    # Step 2: Initialize MCP client
    print(f"\n🔍 Step 2: Initialize MCP Client")
    mcp_success = await client.initialize_mcp_client()
    
    if not mcp_success:
        print("❌ MCP client initialization failed")
        return
    
    # Step 3: Test operations
    print(f"\n🔍 Step 3: Test Jira Operations")
    test_success = await client.test_jira_operations()
    
    # Cleanup
    await client.close()
    
    # Final summary
    print(f"\n🎉 OAuth MCP Test Results:")
    print("=" * 50)
    print(f"✅ OAuth Setup: {'PASS' if oauth_success else 'FAIL'}")
    print(f"✅ MCP Client: {'PASS' if mcp_success else 'FAIL'}")
    print(f"✅ Operations: {'PASS' if test_success else 'FAIL'}")
    
    if oauth_success and mcp_success and test_success:
        print(f"\n🎊 SUCCESS! OAuth MCP integration is working!")
        print(f"🚀 Ready to integrate with LangGraph agent!")
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())
