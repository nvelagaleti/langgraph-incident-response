#!/usr/bin/env python3
"""
Create Task ticket in MYAPPBE project for granularity enhancement
"""

import os
import httpx
from dotenv import load_dotenv

async def create_granularity_task():
    """Create a Task ticket for granularity enhancement in MYAPPBE project."""
    print("🎫 Creating Task ticket in MYAPPBE project...")
    
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL", "https://mailtosimha.atlassian.net")
    access_token = os.getenv("JIRA_OAUTH_ACCESS_TOKEN")
    
    if not access_token:
        print("❌ No access token found")
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
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
                return None
            
            resources = response.json()
            cloud_id = None
            
            for resource in resources:
                if resource.get("url") == jira_url:
                    cloud_id = resource.get("id")
                    break
            
            if not cloud_id:
                print("❌ Could not find cloud ID")
                return None
            
            print(f"✅ Found cloud ID: {cloud_id}")
            
            # Create the task ticket
            issue_data = {
                "fields": {
                    "project": {
                        "key": "MYAPPBE"
                    },
                    "summary": "Add support for second-level granularity in time series data processing",
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Enhance the time series data processing configuration to support second-level granularity for improved data resolution and analysis capabilities."
                                    }
                                ]
                            },
                            {
                                "type": "heading",
                                "attrs": {"level": 2},
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Background"
                                    }
                                ]
                            },
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Currently, the products backend service supports minute-level granularity for time series data processing. This enhancement will extend the system to support second-level granularity, enabling more precise data analysis and monitoring capabilities."
                                    }
                                ]
                            },
                            {
                                "type": "heading",
                                "attrs": {"level": 2},
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Requirements"
                                    }
                                ]
                            },
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "• Extend granularity configuration to support 'second' option\n• Update maxDataPoints calculation for second-level processing (86400 points for 24 hours)\n• Ensure proper memory management for increased data volume\n• Update configuration validation and documentation\n• Add performance monitoring for high-granularity data processing"
                                    }
                                ]
                            },
                            {
                                "type": "heading",
                                "attrs": {"level": 2},
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Technical Implementation"
                                    }
                                ]
                            },
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "• Modify src/config/index.ts to add 'second' to granularity options\n• Update maxDataPoints calculation: 24 hours * 60 minutes * 60 seconds = 86,400 data points\n• Implement memory optimization strategies for large datasets\n• Add configuration validation for granularity settings\n• Update API documentation to reflect new granularity options"
                                    }
                                ]
                            },
                            {
                                "type": "heading",
                                "attrs": {"level": 2},
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Benefits"
                                    }
                                ]
                            },
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "• Higher precision data analysis for time-sensitive applications\n• Better monitoring capabilities for real-time systems\n• Enhanced debugging and troubleshooting with finer granularity\n• Improved data resolution for analytics and reporting"
                                    }
                                ]
                            },
                            {
                                "type": "heading",
                                "attrs": {"level": 2},
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Acceptance Criteria"
                                    }
                                ]
                            },
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "• System accepts 'second' as valid granularity configuration\n• Time series data processing works correctly with second-level granularity\n• Memory usage remains within acceptable limits\n• Performance impact is minimal and documented\n• Configuration validation prevents invalid granularity values\n• Documentation is updated to reflect new capabilities"
                                    }
                                ]
                            }
                        ]
                    },
                    "issuetype": {
                        "name": "Task"
                    },
                    "labels": ["enhancement", "granularity", "time-series", "data-processing"]
                }
            }
            
            response = await client.post(
                f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/issue",
                headers=headers,
                json=issue_data
            )
            
            if response.status_code == 201:
                issue = response.json()
                issue_key = issue.get("key")
                print(f"✅ Task ticket created successfully!")
                print(f"🎫 Ticket ID: {issue_key}")
                print(f"🔗 URL: {jira_url}/browse/{issue_key}")
                return issue
            else:
                print(f"❌ Failed to create ticket: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Error creating ticket: {e}")
        return None

async def main():
    """Main function to create the granularity task ticket."""
    print("🚀 Creating Granularity Enhancement Task")
    print("=" * 60)
    
    issue = await create_granularity_task()
    
    if issue:
        print(f"\n🎊 SUCCESS! Task ticket created in MYAPPBE project")
        print(f"📋 Ticket Details:")
        print(f"   Key: {issue.get('key')}")
        print(f"   ID: {issue.get('id')}")
        print(f"   URL: {os.getenv('JIRA_URL', 'https://mailtosimha.atlassian.net')}/browse/{issue.get('key')}")
    else:
        print("❌ Failed to create task ticket")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
