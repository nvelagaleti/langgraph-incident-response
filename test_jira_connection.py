#!/usr/bin/env python3
"""
Test Jira API connection to debug the 400 Bad Request error
"""

import asyncio
import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_jira_connection():
    """Test Jira API connection and see the actual error response."""
    
    # Get credentials
    access_token = os.getenv("JIRA_OAUTH_ACCESS_TOKEN")
    cloud_id = os.getenv("JIRA_CLOUD_ID", "2d465897-ea50-4081-b4fd-2b7e56d1129c")
    
    print("🧪 Testing Jira API Connection")
    print("="*50)
    print(f"🔑 Access Token: {access_token[:20] if access_token else 'None'}...")
    print(f"☁️  Cloud ID: {cloud_id}")
    
    if not access_token:
        print("❌ No access token found")
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Test 1: Get projects (should work)
    print("\n🔍 Test 1: Getting projects...")
    try:
        url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/project"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            print(f"📊 Status: {response.status_code}")
            if response.status_code == 200:
                projects = response.json()
                print(f"✅ Retrieved {len(projects)} projects")
                for project in projects[:3]:  # Show first 3
                    print(f"   - {project.get('key', 'N/A')}: {project.get('name', 'N/A')}")
            else:
                print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Simple search (should work)
    print("\n🔍 Test 2: Simple search...")
    try:
        url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/search"
        data = {
            "jql": "project in (IR)",
            "maxResults": 5,
            "fields": ["summary", "status"]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            print(f"📊 Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                issues = result.get("issues", [])
                print(f"✅ Retrieved {len(issues)} issues")
                for issue in issues:
                    print(f"   - {issue.get('key', 'N/A')}: {issue.get('fields', {}).get('summary', 'N/A')}")
            else:
                print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Exact issue key search (the problematic one)
    print("\n🔍 Test 3: Exact issue key search...")
    try:
        url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/search"
        data = {
            "jql": 'issuekey = "IR-1"',
            "maxResults": 1,
            "fields": ["summary", "status", "description"]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            print(f"📊 Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                issues = result.get("issues", [])
                print(f"✅ Retrieved {len(issues)} issues")
                for issue in issues:
                    print(f"   - {issue.get('key', 'N/A')}: {issue.get('fields', {}).get('summary', 'N/A')}")
            else:
                print(f"❌ Error: {response.text}")
                print(f"📄 Full response: {response.content}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 4: Try different JQL formats
    print("\n🔍 Test 4: Different JQL formats...")
    jql_tests = [
        'issuekey = "IR-1"',
        'issuekey = IR-1',
        'key = "IR-1"',
        'project = IR AND issuekey = "IR-1"',
        'project in (IR) AND issuekey = "IR-1"'
    ]
    
    for jql in jql_tests:
        try:
            url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/search"
            data = {
                "jql": jql,
                "maxResults": 1,
                "fields": ["summary"]
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                print(f"📊 JQL '{jql}': {response.status_code}")
                if response.status_code != 200:
                    print(f"   ❌ Error: {response.text[:200]}...")
                else:
                    result = response.json()
                    issues = result.get("issues", [])
                    print(f"   ✅ Found {len(issues)} issues")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_jira_connection())
