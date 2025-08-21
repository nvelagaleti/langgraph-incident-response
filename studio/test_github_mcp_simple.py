#!/usr/bin/env python3
"""
Simple test script for GitHub MCP external server.
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_github_mcp():
    """Test GitHub MCP external server."""
    print("🔍 Testing GitHub MCP External Server...")
    
    # Load environment variables
    load_dotenv()
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not github_token:
        print("❌ GitHub token not found")
        return False
    
    print(f"✅ GitHub token found")
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Use the external GitHub MCP server configuration
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
        
        print(f"🔧 Server config: {servers_config}")
        
        # Initialize client
        client = MultiServerMCPClient(servers_config)
        print("✅ MultiServerMCPClient created")
        
        # Get tools
        tools = await client.get_tools()
        print(f"✅ Tools loaded: {len(tools)} tools")
        
        # Show available tools
        print("\n📋 Available GitHub MCP Tools:")
        if isinstance(tools, list):
            for i, tool in enumerate(tools[:10]):  # Show first 10 tools
                print(f"   - Tool {i}: {getattr(tool, 'name', 'Unknown')}")
        else:
            print(f"   - Tools type: {type(tools)}")
        
        print("\n🎉 GitHub MCP test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in GitHub MCP test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_github_mcp())
