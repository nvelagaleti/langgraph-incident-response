#!/usr/bin/env python3
"""
Test the enhanced incident response system with GitHub Copilot MCP integration.
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_enhanced_mcp_integration():
    """Test the enhanced incident response system with MCP integration."""
    print("🔍 Testing Enhanced Incident Response with GitHub Copilot MCP...")
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Import the enhanced incident response system
        from incident_response_enhanced import search_repositories_with_mcp
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Initialize GitHub Copilot MCP client
        github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        if not github_token:
            print("❌ GitHub token not found")
            return False
        
        print("✅ GitHub token found")
        
        # Create MCP client with the same configuration as in incident_response_enhanced.py
        github_mcp_client = MultiServerMCPClient(
            {
                "github": {
                    "url": "https://api.githubcopilot.com/mcp/",
                    "transport": "streamable_http",
                    "headers": {
                        "Authorization": f"Bearer {github_token}",
                        "Accept": "application/vnd.github.v3+json",
                        "Content-Type": "application/json"
                    }
                }
            }
        )
        print("✅ GitHub Copilot MCP client created")
        
        # Test repository search with MCP
        search_keywords = ["products", "web", "frontend"]
        print(f"🔍 Testing repository search with keywords: {search_keywords}")
        
        mcp_repos = await search_repositories_with_mcp(github_mcp_client, search_keywords)
        
        if mcp_repos:
            print(f"✅ MCP repository search successful!")
            print(f"   Found repositories: {mcp_repos}")
        else:
            print("⚠️  MCP repository search returned no results")
        
        print("\n🎉 Enhanced MCP integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing enhanced MCP integration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_enhanced_mcp_integration())
