#!/usr/bin/env python3
"""
Simple OAuth Test for Atlassian MCP
Simplified version with better error handling
"""

import os
import asyncio
import json
import webbrowser
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

def test_oauth_flow():
    """Test OAuth flow step by step."""
    print("🔐 Simple OAuth Test for Atlassian MCP")
    print("=" * 50)
    
    load_dotenv()
    
    # Get credentials
    client_id = os.getenv("JIRA_OAUTH_CLIENT_ID")
    client_secret = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")
    
    if not client_id or not client_secret:
        print("❌ OAuth credentials not found in .env file")
        return False
    
    print(f"✅ Client ID: {client_id[:10]}...")
    print(f"✅ Redirect URI: {redirect_uri}")
    
    # Step 1: Generate authorization URL
    print(f"\n🔹 Step 1: Generate Authorization URL")
    print("-" * 30)
    
    scopes = [
        "read:jira-work",
        "write:jira-work", 
        "read:jira-user",
        "manage:jira-project"
    ]
    
    params = {
        "audience": "api.atlassian.com",
        "client_id": client_id,
        "scope": ",".join(scopes),
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "prompt": "consent"
    }
    
    auth_url = f"https://auth.atlassian.com/authorize?{urlencode(params)}"
    
    print(f"✅ Authorization URL generated:")
    print(f"🔗 {auth_url}")
    print(f"📋 Scopes: {', '.join(scopes)}")
    
    # Step 2: Manual authorization
    print(f"\n🔹 Step 2: Manual Authorization")
    print("-" * 30)
    print(f"🌐 Opening browser for authorization...")
    print(f"📝 After authorization, you'll be redirected to: {redirect_uri}")
    print(f"📋 Copy the 'code' parameter from the URL")
    
    # Open browser
    webbrowser.open(auth_url)
    
    # Get authorization code manually
    print(f"\n⏳ Please complete the authorization in your browser")
    print(f"📋 Then copy the authorization code from the redirect URL")
    auth_code = input("🔑 Enter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return False
    
    print(f"✅ Authorization code received: {auth_code[:10]}...")
    
    # Step 3: Exchange code for token
    print(f"\n🔹 Step 3: Exchange Code for Token")
    print("-" * 30)
    
    token_url = "https://auth.atlassian.com/oauth/token"
    
    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "redirect_uri": redirect_uri
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"📤 Making POST request to: {token_url}")
    
    try:
        response = requests.post(token_url, json=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            print(f"✅ Token exchange successful!")
            print(f"🔑 Access Token: {access_token[:20]}...")
            if refresh_token:
                print(f"🔄 Refresh Token: {refresh_token[:20]}...")
            
            # Save tokens
            os.environ["JIRA_OAUTH_ACCESS_TOKEN"] = access_token
            if refresh_token:
                os.environ["JIRA_OAUTH_REFRESH_TOKEN"] = refresh_token
            
            print(f"💾 Tokens saved to environment variables")
            
            return True
            
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return False

async def test_mcp_integration():
    """Test MCP integration with OAuth token."""
    print(f"\n🔹 Step 4: Test MCP Integration")
    print("-" * 30)
    
    access_token = os.getenv("JIRA_OAUTH_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ No access token available")
        return False
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Configure MCP client
        servers_config = {
            "jira": {
                "transport": "streamable_http",
                "url": "https://mcp.atlassian.com/v1/sse",
                "headers": {
                    "Authorization": f"Bearer {access_token}",
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
        await test_jira_operations(client, tools)
        
        # Close client
        await client.aclose()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize MCP client: {e}")
        return False

async def test_jira_operations(client, tools):
    """Test Jira operations."""
    print(f"\n🔍 Testing Jira Operations")
    print("-" * 20)
    
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
    """Main function."""
    print("🧪 Simple OAuth Test")
    print("=" * 60)
    
    # Step 1-3: OAuth flow
    oauth_success = test_oauth_flow()
    
    if not oauth_success:
        print("❌ OAuth flow failed")
        return
    
    # Step 4: MCP integration
    mcp_success = await test_mcp_integration()
    
    # Final summary
    print(f"\n🎉 OAuth Test Results:")
    print("=" * 50)
    print(f"✅ OAuth Flow: {'PASS' if oauth_success else 'FAIL'}")
    print(f"✅ MCP Integration: {'PASS' if mcp_success else 'FAIL'}")
    
    if oauth_success and mcp_success:
        print(f"\n🎊 SUCCESS! OAuth MCP integration is working!")
        print(f"🚀 Ready to integrate with incident response system!")
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    asyncio.run(main())
