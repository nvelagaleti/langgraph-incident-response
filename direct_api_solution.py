#!/usr/bin/env python3
"""
Direct API Solution - Bypass OAuth issues
Use direct Jira API with API tokens instead of OAuth
"""

import os
import asyncio
import requests
import base64
from dotenv import load_dotenv

def test_direct_api_setup():
    """Test direct API setup with API tokens."""
    print("🔧 Direct API Solution - Bypass OAuth Issues")
    print("=" * 60)
    
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    print(f"✅ Jira URL: {jira_url}")
    print(f"✅ Jira Token: {'Configured' if jira_token else 'Missing'}")
    print(f"✅ Jira Email: {jira_email or 'Missing'}")
    
    if not jira_url or not jira_token:
        print("❌ Jira configuration missing")
        print("💡 You need to get a proper Jira API token")
        return False
    
    # Test different authentication methods
    auth_methods = [
        ("Basic Auth (email:token)", {"Authorization": f"Basic {base64.b64encode(f'{jira_email}:{jira_token}'.encode()).decode()}"} if jira_email else None),
        ("Bearer Token", {"Authorization": f"Bearer {jira_token}"}),
        ("Token Only", {"Authorization": f"token {jira_token}"}),
    ]
    
    headers_base = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    for method_name, auth_header in auth_methods:
        if auth_header is None:
            continue
            
        print(f"\n🔍 Testing: {method_name}")
        try:
            headers = {**headers_base, **auth_header}
            user_url = f"{jira_url}/rest/api/3/myself"
            response = requests.get(user_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ SUCCESS with {method_name}")
                print(f"📄 User: {user_data.get('displayName', 'Unknown')}")
                print(f"📄 Email: {user_data.get('emailAddress', 'Unknown')}")
                
                # Test getting projects
                projects_url = f"{jira_url}/rest/api/3/project"
                projects_response = requests.get(projects_url, headers=headers, timeout=10)
                
                if projects_response.status_code == 200:
                    projects = projects_response.json()
                    project_keys = [proj.get('key', '') for proj in projects if proj.get('key')]
                    print(f"📄 Projects: {len(projects)} found")
                    print(f"📋 Project Keys: {', '.join(project_keys[:5])}")
                
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"📄 Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

def get_proper_jira_token():
    """Guide to get proper Jira API token."""
    print(f"\n🔧 How to Get Proper Jira API Token")
    print("=" * 50)
    
    print(f"📋 Step-by-Step Guide:")
    print(f"1. Go to Atlassian Account Settings:")
    print(f"   https://id.atlassian.com/manage-profile/security/api-tokens")
    print(f"")
    print(f"2. Click 'Create API token'")
    print(f"3. Give it a label: 'Incident Response System'")
    print(f"4. Copy the generated token")
    print(f"")
    print(f"5. Update your .env file:")
    print(f"   JIRA_TOKEN=your_new_api_token_here")
    print(f"   JIRA_EMAIL=your_email@example.com")
    print(f"")
    print(f"6. Run this script again")

async def test_hybrid_integration():
    """Test hybrid GitHub MCP + Direct Jira API integration."""
    print(f"\n🔗 Testing Hybrid Integration")
    print("=" * 50)
    print(f"🔗 GitHub: MCP Integration (working)")
    print(f"🔗 Jira: Direct API Integration")
    
    load_dotenv()
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    
    if not github_token:
        print("❌ GitHub token missing")
        return False
    
    if not jira_url or not jira_token:
        print("❌ Jira configuration missing")
        return False
    
    print(f"✅ GitHub Token: Configured")
    print(f"✅ Jira URL: {jira_url}")
    print(f"✅ Jira Token: Configured")
    
    # Test GitHub MCP (should work)
    print(f"\n🔍 Testing GitHub MCP Integration")
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        servers_config = {
            "github": {
                "transport": "streamable_http",
                "url": "https://api.githubcopilot.com/mcp",
                "headers": {
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }
            }
        }
        
        client = MultiServerMCPClient(servers_config)
        tools = await client.get_tools()
        
        print(f"✅ GitHub MCP: {len(tools)} tools loaded")
        await client.aclose()
        
    except Exception as e:
        print(f"❌ GitHub MCP failed: {e}")
        return False
    
    # Test Jira Direct API
    print(f"\n🔍 Testing Jira Direct API")
    jira_success = test_direct_api_setup()
    
    if jira_success:
        print(f"✅ Jira Direct API: Working")
        print(f"✅ Hybrid Integration: Ready!")
        return True
    else:
        print(f"❌ Jira Direct API: Failed")
        return False

def main():
    """Main function."""
    print("🧪 Direct API Solution")
    print("=" * 60)
    
    # Test current setup
    direct_api_ok = test_direct_api_setup()
    
    if not direct_api_ok:
        print(f"\n❌ Direct API setup failed")
        get_proper_jira_token()
        return
    
    # Test hybrid integration
    hybrid_success = asyncio.run(test_hybrid_integration())
    
    # Final summary
    print(f"\n🎉 Direct API Solution Results:")
    print("=" * 50)
    print(f"✅ Direct API Setup: {'PASS' if direct_api_ok else 'FAIL'}")
    print(f"✅ Hybrid Integration: {'PASS' if hybrid_success else 'FAIL'}")
    
    if direct_api_ok and hybrid_success:
        print(f"\n🎊 SUCCESS! Direct API solution is working!")
        print(f"🚀 Ready to integrate with incident response system!")
        print(f"💡 Benefits:")
        print(f"   - No OAuth complexity")
        print(f"   - Works with API tokens")
        print(f"   - Can handle multiple projects")
        print(f"   - GitHub MCP + Direct Jira API")
    else:
        print(f"\n⚠️  Some tests failed")
        print(f"💡 Get a proper Jira API token and try again")

if __name__ == "__main__":
    main()
