#!/usr/bin/env python3
"""
Test GitHub Copilot MCP Server Access
Tests if we can access the MCP server at https://api.githubcopilot.com/mcp/
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_githubcopilot_mcp_server_health():
    """Test GitHub Copilot MCP server health endpoint."""
    print("🏥 Testing GitHub Copilot MCP Server Health...")
    
    # Load environment variables
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    mcp_url = "https://api.githubcopilot.com/mcp"
    
    if not token:
        print("❌ No GitHub token found in .env file")
        return False
    
    print(f"✅ Token found: {token[:10]}...")
    print(f"✅ MCP Server URL: {mcp_url}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    try:
        # Test health endpoint
        health_url = f"{mcp_url}/health"
        print(f"🔍 Testing health endpoint: {health_url}")
        
        response = requests.get(health_url, headers=headers, timeout=10)
        print(f"📊 Health check response: {response.status_code}")
        
        if response.status_code == 200:
            try:
                health_data = response.json()
                print(f"✅ Server is healthy: {health_data}")
                return True
            except:
                print(f"✅ Server is healthy: {response.text}")
                return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking server health: {e}")
        return False

def test_githubcopilot_mcp_server_tools():
    """Test GitHub Copilot MCP server tools endpoint."""
    print("\n🛠️ Testing GitHub Copilot MCP Server Tools...")
    
    # Load environment variables
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    mcp_url = "https://api.githubcopilot.com/mcp"
    
    if not token:
        print("❌ No GitHub token found in .env file")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    try:
        # Test tools endpoint
        tools_url = f"{mcp_url}/tools"
        print(f"🔍 Testing tools endpoint: {tools_url}")
        
        response = requests.get(tools_url, headers=headers, timeout=10)
        print(f"📊 Tools check response: {response.status_code}")
        
        if response.status_code == 200:
            try:
                tools_data = response.json()
                print(f"✅ Tools available: {len(tools_data.get('tools', []))} tools")
                for tool in tools_data.get('tools', [])[:3]:  # Show first 3 tools
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                return True
            except:
                print(f"✅ Tools endpoint accessible: {response.text}")
                return True
        else:
            print(f"❌ Tools check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking server tools: {e}")
        return False

def test_githubcopilot_mcp_server_endpoints():
    """Test various MCP server endpoints."""
    print("\n🔍 Testing Various MCP Server Endpoints...")
    
    # Load environment variables
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    mcp_url = "https://api.githubcopilot.com/mcp"
    
    if not token:
        print("❌ No GitHub token found in .env file")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    # Test various endpoints
    endpoints = [
        "/",
        "/health",
        "/tools",
        "/capabilities",
        "/resources",
        "/prompts"
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{mcp_url}{endpoint}"
            print(f"🔍 Testing: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Accessible")
            elif response.status_code == 404:
                print(f"   ⚠️  Not found (endpoint doesn't exist)")
            elif response.status_code == 401:
                print(f"   ❌ Unauthorized")
            elif response.status_code == 403:
                print(f"   ❌ Forbidden")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_langchain_mcp_connection():
    """Test LangChain MCP connection to GitHub Copilot's MCP server."""
    print("\n🔌 Testing LangChain MCP Connection to GitHub Copilot's MCP Server...")
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Load environment variables
        load_dotenv()
        
        token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        mcp_url = "https://api.githubcopilot.com/mcp"
        
        if not token:
            print("❌ No GitHub token found in .env file")
            return False
        
        # Configure server
        servers_config = {
            "github": {
                "transport": "streamable_http",
                "url": mcp_url,
                "headers": {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json",
                    "User-Agent": "LangGraph-Incident-Response/1.0"
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

def test_public_github_api():
    """Test if the token works with public GitHub API."""
    print("\n🌐 Testing Public GitHub API Access...")
    
    # Load environment variables
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        print("❌ No GitHub token found in .env file")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    try:
        # Test public GitHub API
        user_url = "https://api.github.com/user"
        print(f"🔍 Testing: {user_url}")
        
        response = requests.get(user_url, headers=headers, timeout=10)
        print(f"📊 Response: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Public GitHub API accessible")
            print(f"   User: {user_data.get('login', 'Unknown')}")
            print(f"   Name: {user_data.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Public GitHub API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing public GitHub API: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 GitHub Copilot MCP Server Test")
    print("=" * 60)
    
    # Test 1: Public GitHub API (to verify token works)
    public_github_ok = test_public_github_api()
    
    # Test 2: MCP server health
    health_ok = test_githubcopilot_mcp_server_health()
    
    # Test 3: MCP server tools
    tools_ok = test_githubcopilot_mcp_server_tools()
    
    # Test 4: Various endpoints
    test_githubcopilot_mcp_server_endpoints()
    
    # Test 5: LangChain MCP connection (if async)
    try:
        import asyncio
        langchain_ok = asyncio.run(test_langchain_mcp_connection())
    except:
        print("\n⚠️  Skipping LangChain MCP connection test (async not available)")
        langchain_ok = False
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    print(f"✅ Public GitHub API: {'PASS' if public_github_ok else 'FAIL'}")
    print(f"✅ MCP Server Health: {'PASS' if health_ok else 'FAIL'}")
    print(f"✅ MCP Server Tools: {'PASS' if tools_ok else 'FAIL'}")
    print(f"✅ LangChain MCP: {'PASS' if langchain_ok else 'FAIL'}")
    
    if public_github_ok and health_ok and tools_ok:
        print("\n🎉 GitHub Copilot MCP server is accessible!")
        print("   You can use it with the LangGraph incident response system.")
    elif public_github_ok:
        print("\n⚠️  Token works with public GitHub but MCP server is not accessible.")
        print("   You may need to use a different MCP server or direct GitHub API.")
    else:
        print("\n❌ Token doesn't work with public GitHub API.")
        print("   Please check your GitHub Personal Access Token.")

if __name__ == "__main__":
    main()
