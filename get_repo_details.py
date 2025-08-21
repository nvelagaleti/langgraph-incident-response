#!/usr/bin/env python3
"""
Get Repository Details
Parse and display detailed information about found repositories
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

async def get_repository_details():
    """Get detailed information about repositories."""
    print("📁 Getting Repository Details")
    print("=" * 50)
    
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    mcp_url = "https://api.githubcopilot.com/mcp"
    
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
        tools = await client.get_tools()
        
        # Find search tool
        search_repos_tool = None
        for tool in tools:
            if hasattr(tool, 'name') and tool.name == 'search_repositories':
                search_repos_tool = tool
                break
        
        if not search_repos_tool:
            print("❌ search_repositories tool not found")
            return
        
        # Search for all your repositories
        print("🔍 Searching for all your repositories...")
        result = await search_repos_tool.ainvoke({
            "query": "user:nvelagaleti"
        })
        
        # Parse the JSON result
        try:
            repo_data = json.loads(result)
            total_count = repo_data.get('total_count', 0)
            items = repo_data.get('items', [])
            
            print(f"✅ Found {total_count} repositories")
            
            if items:
                for i, repo in enumerate(items, 1):
                    print(f"\n📁 Repository {i}:")
                    print(f"   Name: {repo.get('name', 'Unknown')}")
                    print(f"   Full Name: {repo.get('full_name', 'Unknown')}")
                    print(f"   Description: {repo.get('description', 'No description')}")
                    print(f"   URL: {repo.get('html_url', 'Unknown')}")
                    print(f"   Language: {repo.get('language', 'Unknown')}")
                    print(f"   Stars: {repo.get('stargazers_count', 0)}")
                    print(f"   Forks: {repo.get('forks_count', 0)}")
                    print(f"   Private: {repo.get('private', False)}")
                    print(f"   Default Branch: {repo.get('default_branch', 'main')}")
                    print(f"   Created: {repo.get('created_at', 'Unknown')}")
                    print(f"   Updated: {repo.get('updated_at', 'Unknown')}")
                    
                    # Get additional repository details if needed
                    repo_name = repo.get('name')
                    if repo_name:
                        print(f"\n🔍 Getting branches for {repo_name}...")
                        
                        # Find list_branches tool
                        list_branches_tool = None
                        for tool in tools:
                            if hasattr(tool, 'name') and tool.name == 'list_branches':
                                list_branches_tool = tool
                                break
                        
                        if list_branches_tool:
                            try:
                                branches_result = await list_branches_tool.ainvoke({
                                    "owner": "nvelagaleti",
                                    "repo": repo_name
                                })
                                
                                # Parse branches
                                branches_data = json.loads(branches_result)
                                if isinstance(branches_data, list):
                                    branch_names = [branch.get('name', 'Unknown') for branch in branches_data]
                                    print(f"   Branches: {', '.join(branch_names[:5])}")
                                    if len(branches_data) > 5:
                                        print(f"   ... and {len(branches_data) - 5} more")
                                else:
                                    print(f"   Branches: {str(branches_data)[:100]}...")
                                    
                            except Exception as e:
                                print(f"   ❌ Error getting branches: {e}")
            else:
                print("   No repositories found in search results")
                
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON result: {e}")
            print(f"Raw result: {result[:500]}...")
        
        # Search for broader patterns
        print(f"\n🔍 Searching for repositories with broader patterns...")
        
        search_patterns = [
            "nvelagaleti",  # Just username
            "owner:nvelagaleti",  # Different syntax
            "author:nvelagaleti"  # Author syntax
        ]
        
        for pattern in search_patterns:
            try:
                print(f"\n   Pattern: {pattern}")
                result = await search_repos_tool.ainvoke({
                    "query": pattern
                })
                
                repo_data = json.loads(result)
                total_count = repo_data.get('total_count', 0)
                print(f"   Results: {total_count} repositories")
                
                if total_count > 0:
                    items = repo_data.get('items', [])
                    for repo in items[:3]:  # Show first 3
                        print(f"     - {repo.get('full_name', 'Unknown')}")
                        
            except Exception as e:
                print(f"   ❌ Error with pattern '{pattern}': {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(get_repository_details())
