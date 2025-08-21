#!/usr/bin/env python3
"""
Manual OAuth Test for Atlassian MCP
Manual approach without callback server
"""

import os
import asyncio
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

def generate_authorization_url():
    """Generate the authorization URL manually."""
    print("🔐 Manual OAuth Test for Atlassian MCP")
    print("=" * 50)
    
    load_dotenv()
    
    client_id = os.getenv("JIRA_OAUTH_CLIENT_ID")
    redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")
    
    if not client_id:
        print("❌ Client ID not found in .env file")
        return None
    
    # Generate authorization URL
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
    print(f"\n📋 Instructions:")
    print(f"1. Copy the URL above")
    print(f"2. Open it in your browser")
    print(f"3. Log in to Atlassian")
    print(f"4. Authorize the app")
    print(f"5. Copy the 'code' parameter from the redirect URL")
    print(f"6. Paste it below when prompted")
    
    return auth_url

def exchange_code_for_token(auth_code):
    """Exchange authorization code for access token."""
    print(f"\n🔹 Exchanging Code for Token")
    print("-" * 30)
    
    load_dotenv()
    
    client_id = os.getenv("JIRA_OAUTH_CLIENT_ID")
    client_secret = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8080/callback")
    
    if not client_id or not client_secret:
        print("❌ OAuth credentials not found")
        return None
    
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
            
            return access_token
            
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during token exchange: {e}")
        return None

async def test_mcp_with_token(access_token):
    """Test MCP integration with the access token."""
    print(f"\n🔹 Testing MCP Integration")
    print("-" * 30)
    
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
        
        # Close client
        await client.aclose()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize MCP client: {e}")
        return False

def main():
    """Main function."""
    print("🧪 Manual OAuth Test")
    print("=" * 60)
    
    # Step 1: Generate authorization URL
    auth_url = generate_authorization_url()
    if not auth_url:
        return
    
    # Step 2: Get authorization code manually
    print(f"\n⏳ Please complete the authorization in your browser")
    print(f"📋 Then copy the authorization code from the redirect URL")
    auth_code = input("🔑 Enter the authorization code: ").strip()
    
    if not auth_code:
        print("❌ No authorization code provided")
        return
    
    # Step 3: Exchange code for token
    access_token = exchange_code_for_token(auth_code)
    if not access_token:
        return
    
    # Step 4: Test MCP integration
    mcp_success = asyncio.run(test_mcp_with_token(access_token))
    
    # Final summary
    print(f"\n🎉 Manual OAuth Test Results:")
    print("=" * 50)
    print(f"✅ OAuth Flow: {'PASS' if access_token else 'FAIL'}")
    print(f"✅ MCP Integration: {'PASS' if mcp_success else 'FAIL'}")
    
    if access_token and mcp_success:
        print(f"\n🎊 SUCCESS! OAuth MCP integration is working!")
        print(f"🚀 Ready to integrate with incident response system!")
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
