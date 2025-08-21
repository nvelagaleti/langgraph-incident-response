#!/usr/bin/env python3
"""
Test script for external GitHub MCP server functionality.
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.services.mcp_client import mcp_client


async def test_external_github_mcp_setup():
    """Test external GitHub MCP server setup."""
    print("🔍 Testing External GitHub MCP Server Setup...")
    
    # Load environment variables
    load_dotenv()
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    github_mcp_url = os.getenv("MCP_GITHUB_SERVER_URL")
    
    if not github_token:
        print("❌ GitHub token not found in environment")
        print("   Set GITHUB_PERSONAL_ACCESS_TOKEN in your .env file")
        return False
    
    if not github_mcp_url:
        print("❌ GitHub MCP server URL not configured")
        print("   Set MCP_GITHUB_SERVER_URL in your .env file")
        return False
    
    print(f"✅ GitHub token found")
    print(f"✅ GitHub MCP server URL: {github_mcp_url}")
    
    return True


async def test_external_server_connection():
    """Test connection to external GitHub MCP server."""
    print(f"\n🔗 Testing connection to external GitHub MCP server...")
    
    try:
        # Initialize external MCP client
        await mcp_client.initialize_github_mcp(
            external_server_url=os.getenv("MCP_GITHUB_SERVER_URL")
        )
        
        if mcp_client.github_client == "external":
            print("✅ Successfully connected to external GitHub MCP server")
            return True
        else:
            print("❌ Failed to connect to external GitHub MCP server")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to external GitHub MCP server: {e}")
        return False


async def test_external_github_commits():
    """Test getting commits from external GitHub MCP server."""
    print(f"\n📊 Testing commit retrieval from external GitHub MCP server...")
    
    try:
        # Get commits from the last 7 days
        until_date = datetime.now()
        since_date = until_date - timedelta(days=7)
        
        # Test with a sample repository (you can change this)
        test_repo_owner = "github"
        test_repo_name = "github-mcp-server"
        
        print(f"🔍 Testing with repository: {test_repo_owner}/{test_repo_name}")
        
        commits = await mcp_client.get_github_commits(
            since_date=since_date.isoformat(),
            until_date=until_date.isoformat(),
            repo_owner=test_repo_owner,
            repo_name=test_repo_name
        )
        
        print(f"✅ Found {len(commits)} commits from external server")
        
        if commits:
            # Show recent commits
            recent_commits = sorted(commits, key=lambda x: x.date, reverse=True)[:3]
            print("\n📋 Recent Commits:")
            for commit in recent_commits:
                print(f"   - {commit.sha[:8]} by {commit.author}: {commit.message[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting commits from external server: {e}")
        return False


async def test_external_multi_repo():
    """Test multi-repository functionality with external server."""
    print(f"\n🔗 Testing multi-repository functionality with external server...")
    
    try:
        # Test with multiple repositories
        repositories = [
            {"owner": "github", "name": "github-mcp-server"},
            {"owner": "modelcontextprotocol", "name": "spec"}
        ]
        
        # Get commits from the last 3 days
        until_date = datetime.now()
        since_date = until_date - timedelta(days=3)
        
        commits = await mcp_client.get_github_commits_multi_repo(
            since_date=since_date.isoformat(),
            until_date=until_date.isoformat(),
            repositories=repositories
        )
        
        print(f"✅ Found {len(commits)} total commits across repositories")
        
        # Group by repository
        commits_by_repo = {}
        for commit in commits:
            repo = commit.repository
            if repo not in commits_by_repo:
                commits_by_repo[repo] = []
            commits_by_repo[repo].append(commit)
        
        print("\n📋 Commits by Repository:")
        for repo, repo_commits in commits_by_repo.items():
            print(f"   📁 {repo}: {len(repo_commits)} commits")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in multi-repo test: {e}")
        return False


async def test_external_server_health():
    """Test external server health check."""
    print(f"\n🏥 Testing external server health...")
    
    try:
        import httpx
        
        github_mcp_url = os.getenv("MCP_GITHUB_SERVER_URL")
        
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get(f"{github_mcp_url}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ External server is healthy: {health_data}")
                return True
            else:
                print(f"❌ External server health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error checking external server health: {e}")
        return False


async def main():
    """Main test function."""
    print("🧪 External GitHub MCP Server Test")
    print("=" * 50)
    
    # Test 1: Setup and configuration
    setup_ok = await test_external_github_mcp_setup()
    if not setup_ok:
        print("\n❌ External GitHub MCP setup failed")
        return
    
    # Test 2: Server connection
    connection_ok = await test_external_server_connection()
    if not connection_ok:
        print("\n❌ External server connection failed")
        return
    
    # Test 3: Server health
    health_ok = await test_external_server_health()
    if not health_ok:
        print("\n❌ External server health check failed")
        return
    
    # Test 4: Commit retrieval
    commits_ok = await test_external_github_commits()
    if not commits_ok:
        print("\n❌ External commit retrieval failed")
        return
    
    # Test 5: Multi-repo functionality
    multi_repo_ok = await test_external_multi_repo()
    if not multi_repo_ok:
        print("\n❌ External multi-repo functionality failed")
        return
    
    # Summary
    print("\n🎉 External GitHub MCP Server Test Results:")
    print("=" * 50)
    print("✅ Setup and configuration: PASS")
    print("✅ Server connection: PASS")
    print("✅ Server health: PASS")
    print("✅ Commit retrieval: PASS")
    print("✅ Multi-repo functionality: PASS")
    print("\n🚀 External GitHub MCP server is working correctly!")
    
    # Cleanup
    await mcp_client.close()


if __name__ == "__main__":
    asyncio.run(main())
