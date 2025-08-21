#!/usr/bin/env python3
"""
Test Direct Jira API Client
Test the direct Jira API integration without MCP
"""

import os
from src.services.direct_jira_client import direct_jira_client

def test_direct_jira_api():
    """Test direct Jira API client."""
    print("🧪 Testing Direct Jira API Client")
    print("=" * 50)
    
    # Test 1: Authentication
    print("🔍 Test 1: Authentication")
    if not direct_jira_client.authenticate():
        print("❌ Authentication failed")
        return False
    
    print("✅ Authentication successful")
    
    # Test 2: Get Projects
    print(f"\n🔍 Test 2: Get Projects")
    projects = direct_jira_client.get_projects()
    
    if not projects:
        print("❌ No projects found")
        return False
    
    print(f"✅ Found {len(projects)} projects")
    
    # Show project details
    for i, project in enumerate(projects[:5]):
        print(f"   {i+1}. {project.get('key')}: {project.get('name')}")
    
    # Get first project key for testing
    first_project_key = projects[0].get('key') if projects else None
    
    # Test 3: Get Project Details
    if first_project_key:
        print(f"\n🔍 Test 3: Get Project Details ({first_project_key})")
        project_details = direct_jira_client.get_project(first_project_key)
        
        if project_details:
            print(f"✅ Project details retrieved")
            print(f"   Name: {project_details.get('name')}")
            print(f"   Key: {project_details.get('key')}")
            print(f"   Type: {project_details.get('projectTypeKey')}")
    
    # Test 4: Search Issues
    print(f"\n🔍 Test 4: Search Issues")
    issues = direct_jira_client.search_issues("ORDER BY created DESC", max_results=5)
    
    if issues:
        print(f"✅ Found {len(issues)} recent issues")
        for i, issue in enumerate(issues[:3]):
            key = issue.get('key', 'Unknown')
            summary = issue.get('fields', {}).get('summary', 'No summary')
            print(f"   {i+1}. {key}: {summary[:50]}...")
    
    # Test 5: Get Issue Types
    if first_project_key:
        print(f"\n🔍 Test 5: Get Issue Types ({first_project_key})")
        issue_types = direct_jira_client.get_issue_types(first_project_key)
        
        if issue_types:
            print(f"✅ Found {len(issue_types)} issue types")
            for i, issue_type in enumerate(issue_types[:5]):
                print(f"   {i+1}. {issue_type.get('name')} ({issue_type.get('id')})")
    
    # Test 6: Create Test Issue (Simulation)
    print(f"\n🔍 Test 6: Create Test Issue (Simulation)")
    if first_project_key:
        print(f"   🔧 Ready to create issue in project: {first_project_key}")
        print(f"   📋 Would create incident ticket with:")
        print(f"      - Summary: Test Incident: OOM in GraphQL Service")
        print(f"      - Type: Incident")
        print(f"      - Project: {first_project_key}")
        print(f"   ⚠️  Skipping actual creation for safety")
    
    return True

def main():
    """Main function."""
    print("🧪 Direct Jira API Test")
    print("=" * 60)
    
    success = test_direct_jira_api()
    
    # Final summary
    print(f"\n🎉 Direct Jira API Test Results:")
    print("=" * 50)
    print(f"✅ Direct Jira API: {'PASS' if success else 'FAIL'}")
    
    if success:
        print(f"\n🎊 SUCCESS! Direct Jira API is working!")
        print(f"🚀 Ready to integrate with incident response system!")
        print(f"💡 Benefits:")
        print(f"   - No OAuth complexity")
        print(f"   - Full control over Jira operations")
        print(f"   - Works with API tokens")
        print(f"   - Can handle multiple projects")
    else:
        print(f"\n⚠️  Direct Jira API test failed")
        print(f"💡 Check JIRA_TOKEN_FIX.md for setup help")

if __name__ == "__main__":
    main()
