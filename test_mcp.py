#!/usr/bin/env python3
"""
Test script for MCP integration with GitHub and Jira.
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.services.mcp_client import mcp_client


async def test_github_mcp():
    """Test GitHub MCP integration."""
    print("🔍 Testing GitHub MCP Integration...")
    
    github_token = os.getenv("GITHUB_TOKEN")
    github_owner = os.getenv("GITHUB_OWNER")
    github_repo = os.getenv("GITHUB_REPO")
    
    if not all([github_token, github_owner, github_repo]):
        print("❌ GitHub MCP credentials not found in environment")
        print("   Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO")
        return False
    
    try:
        # Initialize GitHub MCP
        await mcp_client.initialize_github_mcp(
            github_token=github_token,
            repo_owner=github_owner,
            repo_name=github_repo
        )
        
        if not mcp_client.github_client:
            print("❌ Failed to initialize GitHub MCP client")
            return False
        
        # Test getting commits
        until_date = datetime.now()
        since_date = until_date - timedelta(days=7)  # Last 7 days
        
        commits = await mcp_client.get_github_commits(
            since_date=since_date.isoformat(),
            until_date=until_date.isoformat()
        )
        
        print(f"✅ GitHub MCP test successful!")
        print(f"   Found {len(commits)} commits in the last 7 days")
        
        if commits:
            latest_commit = commits[0]
            print(f"   Latest commit: {latest_commit.sha[:8]} by {latest_commit.author}")
            print(f"   Message: {latest_commit.message[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ GitHub MCP test failed: {e}")
        return False


async def test_jira_mcp():
    """Test Jira MCP integration."""
    print("\n🔍 Testing Jira MCP Integration...")
    
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_project = os.getenv("JIRA_PROJECT")
    
    if not all([jira_url, jira_token, jira_project]):
        print("❌ Jira MCP credentials not found in environment")
        print("   Set JIRA_URL, JIRA_TOKEN, JIRA_PROJECT")
        return False
    
    try:
        # Initialize Jira MCP
        await mcp_client.initialize_jira_mcp(
            jira_url=jira_url,
            jira_token=jira_token,
            project_key=jira_project
        )
        
        if not mcp_client.jira_client:
            print("❌ Failed to initialize Jira MCP client")
            return False
        
        # Test creating a test issue
        test_summary = f"MCP Test Issue - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        test_description = """
        This is a test issue created by the LangGraph Incident Response System MCP integration.
        
        **Test Details:**
        - Created: {datetime.now()}
        - Purpose: Verify MCP integration
        - Status: Test
        
        This issue will be automatically resolved after testing.
        """
        
        issue_key = await mcp_client.create_jira_issue(
            summary=test_summary,
            description=test_description,
            issue_type="Task"
        )
        
        if issue_key:
            print(f"✅ Jira MCP test successful!")
            print(f"   Created test issue: {issue_key}")
            
            # Add a test comment
            await mcp_client.add_jira_comment(
                issue_key=issue_key,
                comment="MCP integration test completed successfully! 🎉"
            )
            
            # Search for recent issues
            recent_issues = await mcp_client.search_jira_issues(
                jql=f"project = {jira_project} AND created >= -1d ORDER BY created DESC"
            )
            
            print(f"   Found {len(recent_issues)} recent issues in project {jira_project}")
            
            return True
        else:
            print("❌ Failed to create test Jira issue")
            return False
        
    except Exception as e:
        print(f"❌ Jira MCP test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🧪 MCP Integration Test")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Test GitHub MCP
    github_success = await test_github_mcp()
    
    # Test Jira MCP
    jira_success = await test_jira_mcp()
    
    # Summary
    print("\n📊 Test Results:")
    print("=" * 40)
    print(f"GitHub MCP: {'✅ PASS' if github_success else '❌ FAIL'}")
    print(f"Jira MCP:   {'✅ PASS' if jira_success else '❌ FAIL'}")
    
    if github_success and jira_success:
        print("\n🎉 All MCP tests passed! The system is ready for real data integration.")
    else:
        print("\n⚠️  Some MCP tests failed. Check your credentials and try again.")
    
    # Cleanup
    await mcp_client.close()


if __name__ == "__main__":
    asyncio.run(main())

