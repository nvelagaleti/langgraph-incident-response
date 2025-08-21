#!/usr/bin/env python3
"""
Step-by-Step OAuth 2.0 Flow for Atlassian MCP
Follows the exact process: authorize → exchange code → use token
"""

import os
import asyncio
import json
import webbrowser
import requests
from urllib.parse import urlencode, parse_qs, urlparse
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
            print(f"✅ Authorization code received: {auth_code[:10]}...")
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

class AtlassianOAuthFlow:
    """Step-by-step OAuth 2.0 flow for Atlassian."""
    
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("JIRA_OAUTH_CLIENT_ID")
        self.client_secret = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
        self.redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")
        self.auth_url = "https://auth.atlassian.com/authorize"
        self.token_url = "https://auth.atlassian.com/oauth/token"
        self.access_token = None
        self.refresh_token = None
        
    def step_1_generate_authorization_url(self):
        """Step 1: Generate authorization URL."""
        print("🔹 Step 1: Generate Authorization URL")
        print("=" * 50)
        
        # REQUESTED_SCOPES → comma-separated list
        requested_scopes = [
            "read:jira-work",
            "write:jira-work", 
            "read:jira-user",
            "manage:jira-project",
            "manage:jira-configuration",
            "manage:jira-webhook",
            "manage:jira-data-provider"
        ]
        
        params = {
            "audience": "api.atlassian.com",
            "client_id": self.client_id,
            "scope": ",".join(requested_scopes),
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "prompt": "consent"
        }
        
        authorization_url = f"{self.auth_url}?{urlencode(params)}"
        
        print(f"✅ Authorization URL generated:")
        print(f"🔗 {authorization_url}")
        print(f"📋 Scopes: {', '.join(requested_scopes)}")
        
        return authorization_url
    
    async def step_2_initiate_oauth_flow(self, authorization_url):
        """Step 2: Initiate OAuth 2.0 Flow."""
        print(f"\n🔹 Step 2: Initiate OAuth 2.0 Flow")
        print("=" * 50)
        
        # Start callback server
        auth_code_queue = asyncio.Queue()
        
        class Handler(OAuthCallbackHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, auth_code_queue=auth_code_queue, **kwargs)
        
        server = HTTPServer(('localhost', 8080), Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        
        print(f"🌐 Callback server started on port 8080")
        print(f"🌐 Opening browser for authorization...")
        
        try:
            # Open browser
            webbrowser.open(authorization_url)
            
            # Wait for authorization code
            print(f"⏳ Waiting for authorization...")
            auth_code = await asyncio.wait_for(auth_code_queue.get(), timeout=300)
            
            print(f"✅ Authorization code received")
            return auth_code
            
        except asyncio.TimeoutError:
            print(f"❌ Authorization timeout")
            return None
        finally:
            server.shutdown()
    
    def step_3_exchange_code_for_token(self, auth_code):
        """Step 3: Exchange Code for Access Token."""
        print(f"\n🔹 Step 3: Exchange Code for Access Token")
        print("=" * 50)
        
        # Make POST request to Atlassian's token endpoint
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "redirect_uri": self.redirect_uri
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"📤 Making POST request to: {self.token_url}")
        print(f"📋 Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(self.token_url, json=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")
            
            print(f"✅ Token exchange successful!")
            print(f"📋 Response: {json.dumps(token_data, indent=2)}")
            print(f"🔑 Access Token: {self.access_token[:20]}...")
            print(f"🔄 Refresh Token: {self.refresh_token[:20] if self.refresh_token else 'None'}...")
            
            # Save tokens to environment
            os.environ["JIRA_OAUTH_ACCESS_TOKEN"] = self.access_token
            if self.refresh_token:
                os.environ["JIRA_OAUTH_REFRESH_TOKEN"] = self.refresh_token
            
            return True
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
    
    async def step_4_use_oauth_token_in_langgraph(self):
        """Step 4: Use OAuth Token in LangGraph."""
        print(f"\n🔹 Step 4: Use OAuth Token in LangGraph")
        print("=" * 50)
        
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
            
            print(f"🔗 Initializing MCP client with OAuth token")
            print(f"🌐 MCP URL: https://mcp.atlassian.com/v1/sse")
            
            client = MultiServerMCPClient(servers_config)
            tools = await client.get_tools()
            
            print(f"✅ MCP client initialized successfully!")
            print(f"📊 Tools loaded: {len(tools)}")
            
            # Show available tools
            print(f"🔧 Available Tools:")
            for i, tool in enumerate(tools[:10]):
                if hasattr(tool, 'name'):
                    print(f"   {i+1}. {tool.name}")
            
            if len(tools) > 10:
                print(f"   ... and {len(tools) - 10} more tools")
            
            # Test basic operations
            await self.test_jira_operations(client, tools)
            
            # Close client
            await client.aclose()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize MCP client: {e}")
            return False
    
    async def test_jira_operations(self, client, tools):
        """Test Jira operations with OAuth MCP."""
        print(f"\n🔍 Testing Jira Operations")
        print("-" * 30)
        
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

async def main():
    """Main function - execute all OAuth steps."""
    print("🔐 Step-by-Step OAuth 2.0 Flow for Atlassian MCP")
    print("=" * 60)
    
    oauth_flow = AtlassianOAuthFlow()
    
    # Step 1: Generate authorization URL
    auth_url = oauth_flow.step_1_generate_authorization_url()
    
    # Step 2: Initiate OAuth flow
    auth_code = await oauth_flow.step_2_initiate_oauth_flow(auth_url)
    if not auth_code:
        print("❌ OAuth flow failed")
        return
    
    # Step 3: Exchange code for token
    token_success = oauth_flow.step_3_exchange_code_for_token(auth_code)
    if not token_success:
        print("❌ Token exchange failed")
        return
    
    # Step 4: Use OAuth token in LangGraph
    langgraph_success = await oauth_flow.step_4_use_oauth_token_in_langgraph()
    
    # Final summary
    print(f"\n🎉 OAuth Flow Results:")
    print("=" * 50)
    print(f"✅ Step 1 (Authorization URL): PASS")
    print(f"✅ Step 2 (OAuth Flow): PASS")
    print(f"✅ Step 3 (Token Exchange): {'PASS' if token_success else 'FAIL'}")
    print(f"✅ Step 4 (LangGraph Integration): {'PASS' if langgraph_success else 'FAIL'}")
    
    if token_success and langgraph_success:
        print(f"\n🎊 SUCCESS! Complete OAuth flow working!")
        print(f"🚀 Ready to integrate with incident response system!")
        print(f"💡 Your OAuth tokens are saved and ready to use")
    else:
        print(f"\n⚠️  Some steps failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())
