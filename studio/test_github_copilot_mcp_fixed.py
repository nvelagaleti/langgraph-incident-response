#!/usr/bin/env python3
"""
Test GitHub Copilot MCP with the correct configuration.
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_github_copilot_mcp_fixed():
    """Test GitHub Copilot MCP with the working configuration."""
    print("🔍 Testing GitHub Copilot MCP with correct configuration...")
    
    # Load environment variables
    load_dotenv()
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not github_token:
        print("❌ GitHub token not found in environment")
        return False
    
    print(f"✅ GitHub token found")
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Use the correct GitHub Copilot MCP server configuration
        servers_config = {
            "github": {
                "transport": "streamable_http",
                "url": "https://api.githubcopilot.com/mcp/",
                "headers": {
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }
            }
        }
        
        print(f"🔧 Using GitHub Copilot MCP server config")
        print(f"   URL: {servers_config['github']['url']}")
        print(f"   Transport: {servers_config['github']['transport']}")
        
        # Initialize client
        client = MultiServerMCPClient(servers_config)
        print("✅ MultiServerMCPClient created successfully")
        
        # Get tools
        tools = await client.get_tools()
        print(f"✅ Tools loaded: {len(tools)} tools available")
        
        # Show available tools (handle both dict and list formats)
        print("\n📋 Available GitHub Copilot MCP Tools:")
        if isinstance(tools, dict):
            for tool_name, tool in list(tools.items())[:10]:  # Show first 10 tools
                print(f"   - {tool_name}: {tool.name}")
        elif isinstance(tools, list):
            for i, tool in enumerate(tools[:10]):  # Show first 10 tools
                print(f"   - Tool {i}: {getattr(tool, 'name', 'Unknown')}")
        else:
            print(f"   - Tools type: {type(tools)}")
        
        print("\n🎉 GitHub Copilot MCP is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error in GitHub Copilot MCP test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_github_copilot_mcp_fixed())
