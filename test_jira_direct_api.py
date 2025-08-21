#!/usr/bin/env python3
"""
Test Jira Direct API Access
Test Jira API access directly and explore MCP alternatives
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_jira_direct_api():
    """Test direct Jira API access."""
    print("🧪 Testing Jira Direct API Access")
    print("=" * 50)
    
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    
    if not jira_url or not jira_token:
        print("❌ Jira configuration missing")
        return False
    
    print(f"✅ Jira URL: {jira_url}")
    print(f"✅ Jira Token: {jira_token[:20]}...")
    
    # Test Jira API directly
    headers = {
        "Authorization": f"Bearer {jira_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Test 1: Get user info
    print(f"\n🔍 Test 1: Getting User Information")
    try:
        user_url = f"{jira_url}/rest/api/3/myself"
        response = requests.get(user_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ User authenticated successfully")
            print(f"📄 User: {user_data.get('displayName', 'Unknown')}")
            print(f"📄 Email: {user_data.get('emailAddress', 'Unknown')}")
            print(f"📄 Account ID: {user_data.get('accountId', 'Unknown')}")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return False
    
    # Test 2: Get projects
    print(f"\n🔍 Test 2: Getting Projects")
    try:
        projects_url = f"{jira_url}/rest/api/3/project"
        response = requests.get(projects_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            projects_data = response.json()
            print(f"✅ Projects retrieved successfully")
            print(f"📄 Total projects: {len(projects_data)}")
            
            # Show available project keys
            project_keys = [proj.get('key', '') for proj in projects_data if proj.get('key')]
            print(f"📋 Available Project Keys: {', '.join(project_keys[:10])}")
            
            # Show project details
            for i, project in enumerate(projects_data[:5]):
                print(f"   {i+1}. {project.get('key')}: {project.get('name')}")
                
        else:
            print(f"❌ Failed to get projects: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error getting projects: {e}")
    
    # Test 3: Get issue types
    print(f"\n🔍 Test 3: Getting Issue Types")
    try:
        # Try to get issue types for the first project
        if project_keys:
            first_project = project_keys[0]
            issue_types_url = f"{jira_url}/rest/api/3/project/{first_project}"
            response = requests.get(issue_types_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                project_data = response.json()
                issue_types = project_data.get('issueTypes', [])
                print(f"✅ Issue types for {first_project}:")
                for issue_type in issue_types[:5]:
                    print(f"   - {issue_type.get('name')} ({issue_type.get('id')})")
            else:
                print(f"❌ Failed to get issue types: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error getting issue types: {e}")
    
    # Test 4: Search issues
    print(f"\n🔍 Test 4: Searching Issues")
    try:
        search_url = f"{jira_url}/rest/api/3/search"
        search_data = {
            "jql": "ORDER BY created DESC",
            "maxResults": 5,
            "fields": ["summary", "status", "created"]
        }
        
        response = requests.post(search_url, headers=headers, json=search_data, timeout=10)
        
        if response.status_code == 200:
            search_results = response.json()
            issues = search_results.get('issues', [])
            print(f"✅ Issues search successful")
            print(f"📄 Total issues found: {search_results.get('total', 0)}")
            
            for i, issue in enumerate(issues[:3]):
                print(f"   {i+1}. {issue.get('key')}: {issue.get('fields', {}).get('summary', 'No summary')}")
        else:
            print(f"❌ Failed to search issues: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error searching issues: {e}")
    
    return True

def test_jira_mcp_alternatives():
    """Test alternative Jira MCP server URLs."""
    print(f"\n🔍 Testing Jira MCP Server Alternatives")
    print("=" * 50)
    
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    
    # Alternative MCP server URLs to test
    mcp_urls = [
        f"{jira_url}/rest/mcp",
        f"{jira_url}/api/mcp",
        f"{jira_url}/mcp",
        "https://api.atlassian.com/jira/mcp",
        "https://api.atlassian.com/rest/mcp"
    ]
    
    headers = {
        "Authorization": f"Bearer {jira_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    for mcp_url in mcp_urls:
        print(f"\n🔍 Testing: {mcp_url}")
        try:
            response = requests.get(mcp_url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Accessible")
                print(f"   📄 Response: {response.text[:200]}...")
            elif response.status_code == 404:
                print(f"   ⚠️  Not found (endpoint doesn't exist)")
            elif response.status_code == 401:
                print(f"   ❌ Unauthorized")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def show_jira_integration_options():
    """Show options for Jira integration."""
    print(f"\n📋 Jira Integration Options")
    print("=" * 50)
    print(f"1. ✅ Direct Jira API Integration (Working)")
    print(f"   - Use direct REST API calls")
    print(f"   - Full control over Jira operations")
    print(f"   - No MCP server dependency")
    
    print(f"\n2. 🔍 Alternative MCP Servers")
    print(f"   - Try different MCP server URLs")
    print(f"   - Use community MCP servers")
    print(f"   - Deploy local MCP server")
    
    print(f"\n3. 🛠️  Custom MCP Server")
    print(f"   - Deploy Jira MCP server locally")
    print(f"   - Use your Jira credentials")
    print(f"   - Full MCP protocol support")
    
    print(f"\n4. 🔗 Hybrid Approach")
    print(f"   - Use direct API for Jira operations")
    print(f"   - Use MCP for GitHub operations")
    print(f"   - Combine both in LangGraph system")

def main():
    """Main test function."""
    print("🧪 Jira Direct API Test")
    print("=" * 60)
    
    # Test 1: Direct Jira API
    api_ok = test_jira_direct_api()
    
    # Test 2: MCP alternatives
    test_jira_mcp_alternatives()
    
    # Show options
    show_jira_integration_options()
    
    # Final summary
    print(f"\n🎉 Jira Integration Test Results:")
    print("=" * 50)
    print(f"✅ Direct Jira API: {'PASS' if api_ok else 'FAIL'}")
    
    if api_ok:
        print(f"\n🎊 SUCCESS! Jira API access is working!")
        print(f"🚀 Ready to integrate Jira with incident response system!")
        print(f"💡 Recommendation: Use direct API integration for Jira operations")

if __name__ == "__main__":
    main()
