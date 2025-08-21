#!/usr/bin/env python3
"""
Test MCP Toolkit Approach
Using langchain-mcp-adapters to connect to GitHub MCP server
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

async def test_mcp_toolkit_approach():
    """Test the MCP toolkit approach suggested by ChatGPT."""
    print("🧪 Testing MCP Toolkit Approach")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    mcp_url = "https://api.githubcopilot.com/mcp"
    
    if not token:
        print("❌ No GitHub token found in .env file")
        return False
    
    print(f"✅ Token found: {token[:10]}...")
    print(f"✅ MCP Server URL: {mcp_url}")
    
    try:
        # Configure server (similar to MCPToolkit approach)
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
        
        # Initialize client (equivalent to MCPToolkit.from_mcp)
        client = MultiServerMCPClient(servers_config)
        print("✅ MultiServerMCPClient created (equivalent to MCPToolkit)")
        
        # Load tools (equivalent to github_toolkit.tools)
        print("🛠️ Loading MCP tools...")
        tools = await client.get_tools()
        print(f"✅ Tools loaded: {len(tools)} tools")
        
        # Show available tools
        print("\n📋 Available Tools:")
        for tool_name, tool in list(tools.items())[:10]:  # Show first 10 tools
            print(f"   - {tool_name}: {tool.name}")
            if hasattr(tool, 'description'):
                print(f"     Description: {tool.description}")
        
        # Test a specific tool (like getting commits)
        print("\n🔍 Testing GitHub Commits Tool...")
        
        # Look for commit-related tools
        commit_tools = [name for name in tools.keys() if 'commit' in name.lower()]
        if commit_tools:
            print(f"✅ Found commit tools: {commit_tools}")
            
            # Test the first commit tool
            commit_tool = tools[commit_tools[0]]
            print(f"🔧 Testing tool: {commit_tool.name}")
            
            # Try to invoke the tool (this might fail if we need specific parameters)
            try:
                # This is a simplified test - actual invocation would need proper parameters
                print("⚠️  Tool invocation would require specific parameters")
                print("   (This is expected - tools need proper input parameters)")
            except Exception as e:
                print(f"⚠️  Tool invocation test: {e}")
        else:
            print("❌ No commit-related tools found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in MCP toolkit approach: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_alternative_mcp_urls():
    """Test alternative MCP server URLs."""
    print("\n🔍 Testing Alternative MCP Server URLs")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        print("❌ No GitHub token found in .env file")
        return False
    
    # Test different MCP server URLs
    mcp_urls = [
        "https://api.githubcopilot.com/mcp",
        "https://api.github.com/mcp",
        "https://github.com/api/mcp",
        "https://api.github.com/v3/mcp"
    ]
    
    for mcp_url in mcp_urls:
        print(f"\n🔍 Testing: {mcp_url}")
        
        try:
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
            
            client = MultiServerMCPClient(servers_config)
            tools = await client.get_tools()
            
            print(f"✅ SUCCESS: {len(tools)} tools loaded")
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            continue
    
    return False

def test_public_github_api_with_new_token():
    """Test if we can access public GitHub API with a new token."""
    print("\n🌐 Testing Public GitHub API with Current Token")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        print("❌ No GitHub token found in .env file")
        return False
    
    import requests
    
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

async def main():
    """Main test function."""
    print("🧪 MCP Toolkit Approach Test")
    print("=" * 60)
    
    # Test 1: Public GitHub API
    public_github_ok = test_public_github_api_with_new_token()
    
    if not public_github_ok:
        print("\n⚠️  Token doesn't work with public GitHub API.")
        print("   Please generate a new GitHub Personal Access Token with proper permissions.")
        print("   Required scopes: repo, read:org, read:user, read:email")
        return
    
    # Test 2: MCP toolkit approach
    toolkit_ok = await test_mcp_toolkit_approach()
    
    # Test 3: Alternative MCP URLs
    if not toolkit_ok:
        print("\n🔄 Trying alternative MCP server URLs...")
        alternative_ok = await test_alternative_mcp_urls()
        
        if alternative_ok:
            print("✅ Found working MCP server URL!")
        else:
            print("❌ No working MCP server URLs found.")
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    print(f"✅ Public GitHub API: {'PASS' if public_github_ok else 'FAIL'}")
    print(f"✅ MCP Toolkit Approach: {'PASS' if toolkit_ok else 'FAIL'}")
    
    if public_github_ok and toolkit_ok:
        print("\n🎉 MCP toolkit approach works!")
        print("   You can use this with your LangGraph incident response system.")
    elif public_github_ok:
        print("\n⚠️  Token works with public GitHub but MCP server is not accessible.")
        print("   You may need to use direct GitHub API calls instead of MCP.")
    else:
        print("\n❌ Token doesn't work with public GitHub API.")
        print("   Please check your GitHub Personal Access Token.")

if __name__ == "__main__":
    asyncio.run(main())
