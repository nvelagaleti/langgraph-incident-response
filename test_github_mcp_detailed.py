#!/usr/bin/env python3
"""
Detailed test script for GitHub MCP server connection debugging.
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

async def test_github_mcp_server_health():
    """Test GitHub MCP server health endpoint."""
    print("🏥 Testing GitHub MCP Server Health...")
    
    github_mcp_url = os.getenv("MCP_GITHUB_SERVER_URL")
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not github_mcp_url:
        print("❌ MCP_GITHUB_SERVER_URL not configured")
        return False
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            health_url = f"{github_mcp_url.rstrip('/')}/health"
            print(f"🔍 Testing health endpoint: {health_url}")
            
            response = await client.get(health_url, timeout=10.0)
            print(f"📊 Health check response: {response.status_code}")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Server is healthy: {health_data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error checking server health: {e}")
        return False

async def test_github_mcp_server_tools():
    """Test GitHub MCP server tools endpoint."""
    print("\n🛠️ Testing GitHub MCP Server Tools...")
    
    github_mcp_url = os.getenv("MCP_GITHUB_SERVER_URL")
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not github_mcp_url:
        print("❌ MCP_GITHUB_SERVER_URL not configured")
        return False
    
    try:
        async with httpx.AsyncClient() as client:
            # Test tools endpoint
            tools_url = f"{github_mcp_url.rstrip('/')}/tools"
            print(f"🔍 Testing tools endpoint: {tools_url}")
            
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            response = await client.get(tools_url, headers=headers, timeout=10.0)
            print(f"📊 Tools check response: {response.status_code}")
            
            if response.status_code == 200:
                tools_data = response.json()
                print(f"✅ Tools available: {len(tools_data.get('tools', []))} tools")
                for tool in tools_data.get('tools', [])[:3]:  # Show first 3 tools
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                return True
            else:
                print(f"❌ Tools check failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error checking server tools: {e}")
        return False

async def test_github_api_direct():
    """Test direct GitHub API access."""
    print("\n🔗 Testing Direct GitHub API Access...")
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not github_token:
        print("❌ GITHUB_PERSONAL_ACCESS_TOKEN not configured")
        return False
    
    try:
        async with httpx.AsyncClient() as client:
            # Test GitHub API directly
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = await client.get("https://api.github.com/user", headers=headers, timeout=10.0)
            print(f"📊 GitHub API response: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ GitHub API access successful")
                print(f"   User: {user_data.get('login', 'Unknown')}")
                print(f"   Name: {user_data.get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ GitHub API access failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing GitHub API: {e}")
        return False

async def test_langchain_mcp_connection():
    """Test LangChain MCP connection with detailed error handling."""
    print("\n🔌 Testing LangChain MCP Connection...")
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        github_mcp_url = os.getenv("MCP_GITHUB_SERVER_URL")
        github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        
        if not github_mcp_url or not github_token:
            print("❌ GitHub MCP URL or token not configured")
            return False
        
        # Configure server
        servers_config = {
            "github": {
                "transport": "streamable_http",
                "url": github_mcp_url,
                "headers": {
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }
            }
        }
        
        print(f"🔧 Server config: {servers_config}")
        
        # Initialize client
        client = MultiServerMCPClient(servers_config)
        print("✅ MultiServerMCPClient created")
        
        # Get tools
        tools = await client.get_tools()
        print(f"✅ Tools loaded: {len(tools)} tools")
        
        # Show available tools
        for tool_name, tool in list(tools.items())[:5]:  # Show first 5 tools
            print(f"   - {tool_name}: {tool.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in LangChain MCP connection: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🔍 Detailed GitHub MCP Server Test")
    print("=" * 50)
    
    # Test 1: Direct GitHub API access
    github_api_ok = await test_github_api_direct()
    
    # Test 2: MCP server health
    health_ok = await test_github_mcp_server_health()
    
    # Test 3: MCP server tools
    tools_ok = await test_github_mcp_server_tools()
    
    # Test 4: LangChain MCP connection
    langchain_ok = await test_langchain_mcp_connection()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    print(f"✅ Direct GitHub API: {'PASS' if github_api_ok else 'FAIL'}")
    print(f"✅ MCP Server Health: {'PASS' if health_ok else 'FAIL'}")
    print(f"✅ MCP Server Tools: {'PASS' if tools_ok else 'FAIL'}")
    print(f"✅ LangChain MCP: {'PASS' if langchain_ok else 'FAIL'}")
    
    if not github_api_ok:
        print("\n💡 Issue: GitHub token may be invalid or expired")
    elif not health_ok:
        print("\n💡 Issue: MCP server may not be running or URL is incorrect")
    elif not tools_ok:
        print("\n💡 Issue: MCP server may not support the tools endpoint")
    elif not langchain_ok:
        print("\n💡 Issue: LangChain MCP adapter may have compatibility issues")
    else:
        print("\n🎉 All tests passed! GitHub MCP integration is working.")

if __name__ == "__main__":
    asyncio.run(main())
