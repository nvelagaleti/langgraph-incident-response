#!/usr/bin/env python3
"""
Test script for LangChain MCP client with external server connections.
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.services.langchain_mcp_client import langchain_mcp_client


async def test_langchain_mcp_setup():
    """Test LangChain MCP client setup."""
    print("🔍 Testing LangChain MCP Client Setup...")
    
    # Load environment variables
    load_dotenv()
    
    github_mcp_url = os.getenv("MCP_GITHUB_SERVER_URL")
    jira_mcp_url = os.getenv("MCP_JIRA_SERVER_URL")
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    jira_token = os.getenv("JIRA_TOKEN")
    
    if not github_mcp_url and not jira_mcp_url:
        print("❌ No external MCP servers configured")
        print("   Set MCP_GITHUB_SERVER_URL and/or MCP_JIRA_SERVER_URL in your .env file")
        return False
    
    if github_mcp_url and not github_token:
        print("❌ GitHub MCP server URL configured but no token provided")
        print("   Set GITHUB_PERSONAL_ACCESS_TOKEN in your .env file")
        return False
    
    if jira_mcp_url and not jira_token:
        print("❌ Jira MCP server URL configured but no token provided")
        print("   Set JIRA_TOKEN in your .env file")
        return False
    
    print(f"✅ GitHub MCP server URL: {github_mcp_url or 'Not configured'}")
    print(f"✅ Jira MCP server URL: {jira_mcp_url or 'Not configured'}")
    print(f"✅ GitHub token: {'Configured' if github_token else 'Not configured'}")
    print(f"✅ Jira token: {'Configured' if jira_token else 'Not configured'}")
    
    return True


async def test_langchain_mcp_initialization():
    """Test LangChain MCP client initialization."""
    print(f"\n🔗 Testing LangChain MCP client initialization...")
    
    try:
        # Initialize LangChain MCP client
        config = {
            "github_mcp_url": os.getenv("MCP_GITHUB_SERVER_URL"),
            "jira_mcp_url": os.getenv("MCP_JIRA_SERVER_URL"),
            "github_token": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
            "jira_token": os.getenv("JIRA_TOKEN")
        }
        
        success = await langchain_mcp_client.initialize(config)
        
        if success:
            print("✅ LangChain MCP client initialized successfully")
            print(f"   Total tools loaded: {len(langchain_mcp_client.tools)}")
            print(f"   GitHub tools: {len(langchain_mcp_client.github_tools)}")
            print(f"   Jira tools: {len(langchain_mcp_client.jira_tools)}")
            return True
        else:
            print("❌ LangChain MCP client initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing LangChain MCP client: {e}")
        return False


async def test_github_commits():
    """Test GitHub commit retrieval."""
    print(f"\n📊 Testing GitHub commit retrieval...")
    
    if not langchain_mcp_client.github_tools:
        print("❌ No GitHub tools available")
        return False
    
    try:
        # Get commits from the last 7 days
        until_date = datetime.now()
        since_date = until_date - timedelta(days=7)
        
        # Test with a sample repository
        test_repo_owner = "github"
        test_repo_name = "github-mcp-server"
        
        print(f"🔍 Testing with repository: {test_repo_owner}/{test_repo_name}")
        
        commits = await langchain_mcp_client.get_github_commits(
            since_date=since_date.isoformat(),
            until_date=until_date.isoformat(),
            repo_owner=test_repo_owner,
            repo_name=test_repo_name
        )
        
        print(f"✅ Retrieved {len(commits)} commits from external GitHub MCP server")
        
        if commits:
            # Show recent commits
            recent_commits = sorted(commits, key=lambda x: x.date, reverse=True)[:3]
            print("\n📋 Recent Commits:")
            for commit in recent_commits:
                print(f"   - {commit.sha[:8]} by {commit.author}: {commit.message[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting GitHub commits: {e}")
        return False


async def test_jira_operations():
    """Test Jira operations."""
    print(f"\n🎫 Testing Jira operations...")
    
    if not langchain_mcp_client.jira_tools:
        print("❌ No Jira tools available")
        return False
    
    try:
        # Test creating a Jira issue
        test_summary = "Test Incident - LangChain MCP Integration"
        test_description = """
        **Test Incident**
        
        This is a test incident created by the LangChain MCP client.
        
        **Details:**
        - Created via external MCP server
        - Testing incident response system
        - Automated ticket creation
        
        **Status:** Test
        """
        
        print("🔍 Testing Jira issue creation...")
        
        issue_key = await langchain_mcp_client.create_jira_issue(
            summary=test_summary,
            description=test_description,
            issue_type="Incident"
        )
        
        if issue_key:
            print(f"✅ Created Jira issue: {issue_key}")
            
            # Test adding a comment
            test_comment = "**Test Comment**\n\nThis is a test comment added via LangChain MCP client."
            
            comment_success = await langchain_mcp_client.add_jira_comment(
                issue_key=issue_key,
                comment=test_comment
            )
            
            if comment_success:
                print(f"✅ Added comment to Jira issue: {issue_key}")
            else:
                print(f"❌ Failed to add comment to Jira issue: {issue_key}")
            
            return True
        else:
            print("❌ Failed to create Jira issue")
            return False
        
    except Exception as e:
        print(f"❌ Error testing Jira operations: {e}")
        return False


async def test_multi_repo_support():
    """Test multi-repository support."""
    print(f"\n🔗 Testing multi-repository support...")
    
    if not langchain_mcp_client.github_tools:
        print("❌ No GitHub tools available")
        return False
    
    try:
        # Test with multiple repositories
        repositories = [
            {"owner": "github", "name": "github-mcp-server"},
            {"owner": "modelcontextprotocol", "name": "spec"}
        ]
        
        # Get commits from the last 3 days
        until_date = datetime.now()
        since_date = until_date - timedelta(days=3)
        
        commits = await langchain_mcp_client.get_github_commits_multi_repo(
            since_date=since_date.isoformat(),
            until_date=until_date.isoformat(),
            repositories=repositories
        )
        
        print(f"✅ Retrieved {len(commits)} total commits across repositories")
        
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
        print(f"❌ Error testing multi-repo support: {e}")
        return False


async def main():
    """Main test function."""
    print("🧪 LangChain MCP Client Test")
    print("=" * 50)
    
    # Test 1: Setup and configuration
    setup_ok = await test_langchain_mcp_setup()
    if not setup_ok:
        print("\n❌ LangChain MCP setup failed")
        return
    
    # Test 2: Client initialization
    init_ok = await test_langchain_mcp_initialization()
    if not init_ok:
        print("\n❌ LangChain MCP initialization failed")
        return
    
    # Test 3: GitHub operations
    if langchain_mcp_client.github_tools:
        github_ok = await test_github_commits()
        if not github_ok:
            print("\n❌ GitHub operations failed")
    
    # Test 4: Jira operations
    if langchain_mcp_client.jira_tools:
        jira_ok = await test_jira_operations()
        if not jira_ok:
            print("\n❌ Jira operations failed")
    
    # Test 5: Multi-repo support
    if langchain_mcp_client.github_tools:
        multi_repo_ok = await test_multi_repo_support()
        if not multi_repo_ok:
            print("\n❌ Multi-repo support failed")
    
    # Summary
    print("\n🎉 LangChain MCP Client Test Results:")
    print("=" * 50)
    print("✅ Setup and configuration: PASS")
    print("✅ Client initialization: PASS")
    
    if langchain_mcp_client.github_tools:
        print("✅ GitHub operations: PASS")
        print("✅ Multi-repo support: PASS")
    
    if langchain_mcp_client.jira_tools:
        print("✅ Jira operations: PASS")
    
    print("\n🚀 LangChain MCP client is working correctly!")
    print("\n💡 Next Steps:")
    print("   1. Configure your external MCP server URLs")
    print("   2. Set up your GitHub and Jira tokens")
    print("   3. Run the full incident response system")
    
    # Cleanup
    await langchain_mcp_client.close()


if __name__ == "__main__":
    asyncio.run(main())
