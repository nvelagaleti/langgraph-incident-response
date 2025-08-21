#!/usr/bin/env python3
"""
Check available issue types in IR project
"""

import os
import httpx
from dotenv import load_dotenv

async def check_issue_types():
    """Check available issue types in the IR project."""
    print("🔍 Checking available issue types in IR project...")
    
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL", "https://mailtosimha.atlassian.net")
    access_token = os.getenv("JIRA_OAUTH_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ No access token found")
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # First get cloud ID
            response = await client.get(
                "https://api.atlassian.com/oauth/token/accessible-resources",
                headers=headers
            )
            
            if response.status_code != 200:
                print(f"❌ Failed to get cloud ID: {response.status_code}")
                return
            
            resources = response.json()
            cloud_id = None
            
            for resource in resources:
                if resource.get("url") == jira_url:
                    cloud_id = resource.get("id")
                    break
            
            if not cloud_id:
                print("❌ Could not find cloud ID")
                return
            
            print(f"✅ Found cloud ID: {cloud_id}")
            
            # Get issue types for IR project
            response = await client.get(
                f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/project/IR",
                headers=headers
            )
            
            if response.status_code == 200:
                project_data = response.json()
                print(f"✅ Project data retrieved")
                print(f"📋 Project Key: {project_data.get('key')}")
                print(f"📋 Project Name: {project_data.get('name')}")
                
                # Get issue types
                response = await client.get(
                    f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/project/IR",
                    headers=headers
                )
                
                if response.status_code == 200:
                    project_info = response.json()
                    issue_types = project_info.get('issueTypes', [])
                    
                    print(f"\n📋 Available Issue Types:")
                    print("=" * 50)
                    for issue_type in issue_types:
                        print(f"   • {issue_type.get('name')} (ID: {issue_type.get('id')})")
                        print(f"     Description: {issue_type.get('description', 'No description')}")
                        print()
                
            else:
                print(f"❌ Failed to get project info: {response.status_code}")
                print(f"Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_issue_types())
