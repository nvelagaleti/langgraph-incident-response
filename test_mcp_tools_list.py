#!/usr/bin/env python3
"""
List MCP Tools
Show the available tools from the GitHub Copilot MCP server
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

async def list_mcp_tools():
    """List all available MCP tools."""
    print("🛠️ Listing GitHub Copilot MCP Tools")
    print("=" * 50)
    
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    mcp_url = "https://api.githubcopilot.com/mcp"
    
    if not token:
        print("❌ No token found")
        return
    
    try:
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
        
        # Initialize client
        client = MultiServerMCPClient(servers_config)
        print("✅ MultiServerMCPClient created")
        
        # Get tools
        tools = await client.get_tools()
        print(f"✅ Tools loaded: {len(tools)} tools")
        
        # Show available tools
        print("\n📋 Available MCP Tools:")
        print("-" * 50)
        
        if isinstance(tools, dict):
            # If tools is a dictionary
            for i, (tool_name, tool) in enumerate(tools.items(), 1):
                print(f"{i:2d}. {tool_name}")
                if hasattr(tool, 'description'):
                    print(f"    Description: {tool.description}")
                if hasattr(tool, 'name'):
                    print(f"    Name: {tool.name}")
                print()
        elif isinstance(tools, list):
            # If tools is a list
            for i, tool in enumerate(tools, 1):
                if hasattr(tool, 'name'):
                    print(f"{i:2d}. {tool.name}")
                else:
                    print(f"{i:2d}. {str(tool)[:50]}...")
                
                if hasattr(tool, 'description'):
                    print(f"    Description: {tool.description}")
                print()
        
        # Look for commit-related tools
        print("\n🔍 Commit-Related Tools:")
        print("-" * 30)
        
        commit_tools = []
        if isinstance(tools, dict):
            commit_tools = [name for name in tools.keys() if 'commit' in name.lower()]
        elif isinstance(tools, list):
            commit_tools = [tool.name for tool in tools if hasattr(tool, 'name') and 'commit' in tool.name.lower()]
        
        if commit_tools:
            for tool in commit_tools:
                print(f"  ✅ {tool}")
        else:
            print("  ⚠️ No explicit commit tools found")
        
        # Look for repository-related tools
        print("\n📁 Repository-Related Tools:")
        print("-" * 30)
        
        repo_tools = []
        if isinstance(tools, dict):
            repo_tools = [name for name in tools.keys() if any(keyword in name.lower() for keyword in ['repo', 'repository', 'git'])]
        elif isinstance(tools, list):
            repo_tools = [tool.name for tool in tools if hasattr(tool, 'name') and any(keyword in tool.name.lower() for keyword in ['repo', 'repository', 'git'])]
        
        if repo_tools:
            for tool in repo_tools[:10]:  # Show first 10
                print(f"  ✅ {tool}")
        else:
            print("  ⚠️ No explicit repository tools found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(list_mcp_tools())
