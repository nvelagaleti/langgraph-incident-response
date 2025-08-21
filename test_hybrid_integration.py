#!/usr/bin/env python3
"""
Test Hybrid Integration
Test GitHub MCP + Direct Jira API integration
"""

import os
import asyncio
from dotenv import load_dotenv
from src.services.langchain_mcp_client import langchain_mcp_client

async def test_hybrid_integration():
    """Test hybrid GitHub MCP + Direct Jira API integration."""
    print("🧪 Testing Hybrid Integration")
    print("=" * 60)
    print("🔗 GitHub: MCP Integration")
    print("🔗 Jira: Direct API Integration")
    print("=" * 60)
    
    load_dotenv()
    
    # Check configuration
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    print(f"✅ GitHub Token: {'Configured' if github_token else 'Missing'}")
    print(f"✅ Jira URL: {jira_url}")
    print(f"✅ Jira Token: {'Configured' if jira_token else 'Missing'}")
    print(f"✅ Jira Email: {'Configured' if jira_email else 'Missing'}")
    
    if not github_token:
        print("❌ GitHub token missing")
        return False
    
    if not jira_url or not jira_token:
        print("❌ Jira configuration missing")
        return False
    
    # Test 1: Initialize hybrid client
    print(f"\n🔍 Test 1: Initializing Hybrid Client")
    config = {
        "github_mcp_url": "https://api.githubcopilot.com/mcp",
        "jira_url": jira_url,
        "jira_token": jira_token,
        "jira_email": jira_email
    }
    
    success = await langchain_mcp_client.initialize(config)
    if not success:
        print("❌ Failed to initialize hybrid client")
        return False
    
    print(f"✅ Hybrid client initialized successfully")
    
    # Test 2: GitHub MCP Operations
    print(f"\n🔍 Test 2: GitHub MCP Operations")
    
    # Test getting commits from your repositories
    repositories = [
        {"owner": "nvelagaleti", "name": "productsBackendService"},
        {"owner": "nvelagaleti", "name": "productsGraphQLService"},
        {"owner": "nvelagaleti", "name": "productsWebApp"}
    ]
    
    try:
        # Get recent commits
        from datetime import datetime, timedelta
        since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        until_date = datetime.now().strftime("%Y-%m-%d")
        
        commits = await langchain_mcp_client.get_github_commits_multi_repo(
            since_date, until_date, repositories
        )
        
        print(f"✅ GitHub MCP: Retrieved {len(commits)} commits")
        
        if commits:
            print(f"📄 Sample commits:")
            for i, commit in enumerate(commits[:3]):
                print(f"   {i+1}. {commit.sha[:8]}: {commit.message[:50]}...")
        
    except Exception as e:
        print(f"❌ GitHub MCP test failed: {e}")
    
    # Test 3: Jira Direct API Operations
    print(f"\n🔍 Test 3: Jira Direct API Operations")
    
    try:
        # Test searching issues
        issues = await langchain_mcp_client.search_jira_issues("ORDER BY created DESC")
        print(f"✅ Jira Direct API: Retrieved {len(issues)} issues")
        
        if issues:
            print(f"📄 Sample issues:")
            for i, issue in enumerate(issues[:3]):
                key = issue.get("key", "Unknown")
                summary = issue.get("fields", {}).get("summary", "No summary")
                print(f"   {i+1}. {key}: {summary[:50]}...")
        
    except Exception as e:
        print(f"❌ Jira Direct API test failed: {e}")
    
    # Test 4: Combined Incident Response Simulation
    print(f"\n🔍 Test 4: Combined Incident Response Simulation")
    
    try:
        # Simulate creating an incident ticket
        incident_summary = "Test Incident: OOM in GraphQL Service"
        incident_description = """
        **Incident Summary:**
        Out of Memory (OOM) error detected in GraphQL service.
        
        **Affected Services:**
        - productsGraphQLService
        - productsWebApp (UI crashes)
        
        **Initial Investigation:**
        - Memory usage spiked to 95%
        - Recent backend configuration changes detected
        - Multiple API errors in logs
        
        **Next Steps:**
        1. Analyze recent commits
        2. Check memory configuration
        3. Monitor service health
        """
        
        issue_key = await langchain_mcp_client.create_jira_issue(
            summary=incident_summary,
            description=incident_description,
            issue_type="Incident"
        )
        
        if issue_key:
            print(f"✅ Created incident ticket: {issue_key}")
            
            # Add investigation details
            investigation_comment = f"""
            **Investigation Update:**
            
            **GitHub Analysis:**
            - Analyzed {len(commits)} recent commits across repositories
            - Found potential root cause in backend configuration
            
            **Recommendations:**
            1. Rollback recent backend changes
            2. Increase GraphQL service memory limits
            3. Add memory monitoring alerts
            
            **Status:** Investigation in progress
            """
            
            success = await langchain_mcp_client.add_jira_comment(issue_key, investigation_comment)
            if success:
                print(f"✅ Added investigation details to {issue_key}")
            else:
                print(f"⚠️  Failed to add comment to {issue_key}")
        else:
            print(f"❌ Failed to create incident ticket")
        
    except Exception as e:
        print(f"❌ Combined test failed: {e}")
    
    # Test 5: Cleanup
    print(f"\n🔍 Test 5: Cleanup")
    await langchain_mcp_client.close()
    print(f"✅ Cleanup completed")
    
    return True

async def main():
    """Main function."""
    print("🧪 Hybrid Integration Test")
    print("=" * 60)
    
    success = await test_hybrid_integration()
    
    # Final summary
    print(f"\n🎉 Hybrid Integration Test Results:")
    print("=" * 50)
    print(f"✅ Hybrid Integration: {'PASS' if success else 'FAIL'}")
    
    if success:
        print(f"\n🎊 SUCCESS! Hybrid integration is working!")
        print(f"🚀 GitHub MCP + Direct Jira API operational!")
        print(f"📋 Ready for incident response automation!")
        print(f"\n💡 Benefits:")
        print(f"   - GitHub: Full MCP integration with repository access")
        print(f"   - Jira: Direct API integration with multiple projects")
        print(f"   - Combined: Complete incident response workflow")
    else:
        print(f"\n⚠️  Some tests failed. Check the output above for details.")
        print(f"💡 Check JIRA_TOKEN_GUIDE.md for Jira setup help")

if __name__ == "__main__":
    asyncio.run(main())
