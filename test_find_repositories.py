#!/usr/bin/env python3
"""
Find Repositories using GitHub Copilot MCP Server
Test repository search and listing functionality
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

async def find_repositories():
    """Find and list repositories using MCP tools."""
    print("🔍 Finding Repositories using GitHub Copilot MCP Server")
    print("=" * 60)
    
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
        
        # Find repository-related tools
        search_repos_tool = None
        for tool in tools:
            if hasattr(tool, 'name') and tool.name == 'search_repositories':
                search_repos_tool = tool
                break
        
        if not search_repos_tool:
            print("❌ search_repositories tool not found")
            return
        
        print(f"✅ Found search_repositories tool: {search_repos_tool.name}")
        print(f"📝 Description: {search_repos_tool.description}")
        
        # Test 1: Search for your own repositories
        print("\n🔍 Test 1: Searching for your repositories...")
        try:
            # Search for repositories by the authenticated user
            result = await search_repos_tool.ainvoke({
                "query": "user:nvelagaleti"
            })
            print("✅ Search completed")
            print(f"📊 Result type: {type(result)}")
            print(f"📄 Result: {str(result)[:500]}...")
            
        except Exception as e:
            print(f"❌ Error in search: {e}")
        
        # Test 2: Search for specific repositories
        print("\n🔍 Test 2: Searching for specific repositories...")
        search_terms = [
            "oopsOps",
            "langchain-academy", 
            "incident-response",
            "microservices"
        ]
        
        for term in search_terms:
            try:
                print(f"\n   Searching for: {term}")
                result = await search_repos_tool.ainvoke({
                    "query": f"{term} user:nvelagaleti"
                })
                print(f"   ✅ Search for '{term}' completed")
                print(f"   📄 Result: {str(result)[:200]}...")
                
            except Exception as e:
                print(f"   ❌ Error searching for '{term}': {e}")
        
        # Test 3: Get user info
        print("\n👤 Test 3: Getting user information...")
        get_me_tool = None
        for tool in tools:
            if hasattr(tool, 'name') and tool.name == 'get_me':
                get_me_tool = tool
                break
        
        if get_me_tool:
            try:
                user_info = await get_me_tool.ainvoke({})
                print("✅ User info retrieved")
                print(f"📄 User info: {str(user_info)[:300]}...")
                
            except Exception as e:
                print(f"❌ Error getting user info: {e}")
        else:
            print("❌ get_me tool not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(find_repositories())
