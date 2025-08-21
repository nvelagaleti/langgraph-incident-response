#!/usr/bin/env python3
"""
Jira Token Validation
Simple script to test Jira token authentication
"""

import os
import requests
import base64
from dotenv import load_dotenv

def test_jira_token():
    """Test Jira token authentication."""
    print("🧪 Jira Token Validation")
    print("=" * 40)
    
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    if not jira_url or not jira_token:
        print("❌ Missing Jira configuration")
        return False
    
    print(f"✅ Jira URL: {jira_url}")
    print(f"✅ Jira Token: {jira_token[:20]}...")
    if jira_email:
        print(f"✅ Jira Email: {jira_email}")
    
    # Test different authentication methods
    auth_methods = [
        ("Bearer Token", {"Authorization": f"Bearer {jira_token}"}),
        ("Basic Auth", {"Authorization": f"Basic {base64.b64encode(f'{jira_email}:{jira_token}'.encode()).decode()}"} if jira_email else None),
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
                print(f"✅ SUCCESS!")
                print(f"📄 User: {user_data.get('displayName', 'Unknown')}")
                print(f"📄 Email: {user_data.get('emailAddress', 'Unknown')}")
                print(f"📄 Account ID: {user_data.get('accountId', 'Unknown')}")
                
                # Test getting projects
                projects_url = f"{jira_url}/rest/api/3/project"
                projects_response = requests.get(projects_url, headers=headers, timeout=10)
                
                if projects_response.status_code == 200:
                    projects = projects_response.json()
                    project_keys = [proj.get('key', '') for proj in projects if proj.get('key')]
                    print(f"📄 Projects: {len(projects)} found")
                    print(f"📋 Project Keys: {', '.join(project_keys[:5])}")
                else:
                    print(f"⚠️  Could not get projects: {projects_response.status_code}")
                
                return True
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"📄 Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n❌ No authentication method worked")
    print(f"💡 Please check the JIRA_TOKEN_GUIDE.md for help")
    return False

def main():
    """Main function."""
    success = test_jira_token()
    
    if success:
        print(f"\n🎉 SUCCESS! Jira token is working!")
        print(f"🚀 Ready to integrate with incident response system!")
    else:
        print(f"\n⚠️  Jira token validation failed")
        print(f"📖 Check JIRA_TOKEN_GUIDE.md for setup instructions")

if __name__ == "__main__":
    main()
