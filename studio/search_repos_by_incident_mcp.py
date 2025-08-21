#!/usr/bin/env python3
"""
Search repositories using incident keywords via GitHub MCP.
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

async def search_repos_by_incident_mcp():
    """Search repositories using incident keywords via GitHub MCP."""
    print("🔍 Searching repositories using incident keywords via GitHub MCP...")
    
    # Load environment variables
    load_dotenv()
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not github_token:
        print("❌ GitHub token not found")
        return False
    
    print(f"✅ GitHub token found")
    
    # Incident keywords extracted from the description
    incident_keywords = [
        "UI", "web application", "product", "GraphQL", "service", 
        "frontend", "backend", "products", "microservices", "API"
    ]
    
    try:
        # Initialize GitHub MCP client
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
        
        print("🔧 Initializing GitHub MCP client...")
        client = MultiServerMCPClient(servers_config)
        print("✅ GitHub MCP client initialized")
        
        # Get available tools
        tools = await client.get_tools()
        print(f"✅ Found {len(tools)} MCP tools")
        
        # Show available tools (following the working pattern)
        print("\n📋 Available GitHub MCP Tools:")
        repo_tools = []
        if isinstance(tools, list):
            for i, tool in enumerate(tools):
                tool_name = getattr(tool, 'name', 'Unknown')
                print(f"   - Tool {i}: {tool_name}")
                # Look for repository-related tools
                if any(keyword in tool_name.lower() for keyword in ['repo', 'repository', 'search', 'list']):
                    repo_tools.append((tool_name, tool))
        else:
            print(f"   - Tools type: {type(tools)}")
        
        print(f"🔍 Found {len(repo_tools)} repository-related tools")
        
        if repo_tools:
            print("\n📋 Available repository tools:")
            for i, (tool_name, tool) in enumerate(repo_tools):
                print(f"   {i+1}. {tool_name}")
            
            # Try to use MCP tools to get repositories
            found_repos = []
            
            for tool_name, tool in repo_tools:
                try:
                    print(f"\n🔍 Trying tool: {tool_name}")
                    
                    # Try to invoke the tool to get repositories (following working pattern)
                    if 'search_repositories' in tool_name.lower():
                        # Try searching with keywords
                        for keyword in incident_keywords[:3]:  # Use top 3 keywords
                            try:
                                result = await tool.ainvoke({"query": f"user:nvelagaleti {keyword}"})
                                print(f"   ✅ Search result for '{keyword}': {result}")
                                if result and isinstance(result, dict) and 'items' in result:
                                    repos = result['items']
                                    for repo in repos:
                                        if isinstance(repo, dict):
                                            found_repos.append(repo)
                            except Exception as e:
                                print(f"   ⚠️  Search failed for '{keyword}': {e}")
                    
                    elif 'list' in tool_name.lower():
                        # Try listing with different approaches
                        try:
                            result = await tool.ainvoke({})
                            print(f"   ✅ List result: {result}")
                            if result and isinstance(result, list):
                                found_repos.extend(result)
                        except Exception as e:
                            print(f"   ⚠️  List failed: {e}")
                    
                except Exception as e:
                    print(f"   ❌ Tool invocation failed: {e}")
            
            # Process found repositories
            if found_repos:
                print(f"\n🎯 Found {len(found_repos)} repositories via MCP:")
                for i, repo in enumerate(found_repos, 1):
                    if isinstance(repo, dict):
                        repo_name = repo.get('name', repo.get('full_name', 'Unknown'))
                        repo_description = repo.get('description', 'No description')
                        repo_language = repo.get('language', 'Unknown')
                        print(f"   {i}. {repo_name}")
                        print(f"       Language: {repo_language}")
                        if repo_description:
                            print(f"       Description: {repo_description}")
                    else:
                        print(f"   {i}. {repo}")
                return found_repos
            else:
                print("⚠️  No repositories found via MCP tools")
                return []
        else:
            print("⚠️  No repository tools available in MCP")
            return []
            
    except Exception as e:
        print(f"❌ Error with GitHub MCP: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(search_repos_by_incident_mcp())
