#!/usr/bin/env python3
"""
Create IR Ticket using existing OAuth token
"""

import os
import json
import httpx
from dotenv import load_dotenv
from datetime import datetime

class IRTicketCreator:
    def __init__(self):
        load_dotenv()
        self.jira_url = os.getenv("JIRA_URL", "https://mailtosimha.atlassian.net")
        self.access_token = os.getenv("JIRA_OAUTH_ACCESS_TOKEN")
        self.project_key = "IR"  # IR Project
        
        if not self.access_token:
            raise ValueError("No access token found in environment")
    
    async def get_cloud_id(self):
        """Get the cloud ID for the Atlassian instance."""
        print("🔍 Getting cloud ID...")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.atlassian.com/oauth/token/accessible-resources",
                    headers=headers
                )
                
                if response.status_code == 200:
                    resources = response.json()
                    for resource in resources:
                        if resource.get("url") == self.jira_url:
                            cloud_id = resource.get("id")
                            print(f"✅ Found cloud ID: {cloud_id}")
                            return cloud_id
                    
                    print("❌ Could not find cloud ID for the Jira URL")
                    return None
                else:
                    print(f"❌ Failed to get cloud ID: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error getting cloud ID: {e}")
            return None
    
    async def create_issue(self, cloud_id):
        """Create the IR ticket."""
        print("🎫 Creating IR ticket...")
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        issue_data = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": "Products Web Application - GraphQL Service Connection Failure",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Customer reports UI failure when attempting to view product data. Web application loads successfully but fails to display product information due to GraphQL service connection issues."
                                }
                            ]
                        },
                        {
                            "type": "heading",
                            "attrs": {"level": 2},
                            "content": [
                                {
                                    "type": "text",
                                    "text": "User Experience"
                                }
                            ]
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "• Web application loads at http://localhost:3001\n• Application interface appears normal initially\n• Product list fails to populate when data is requested\n• UI displays error message or loading failure\n• User cannot view or interact with product information"
                                }
                            ]
                        },
                        {
                            "type": "heading",
                            "attrs": {"level": 2},
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Technical Details"
                                }
                            ]
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "• Frontend: React + Vite (Port 3001)\n• Backend: Express.js REST API (Port 3000)\n• GraphQL Gateway: Apollo Server (Port 4000)\n• Issue: GraphQL service appears to be down - connection refused"
                                }
                            ]
                        },
                        {
                            "type": "heading",
                            "attrs": {"level": 2},
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Investigation Required"
                                }
                            ]
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "• GraphQL Service Status: Verify if service is running and responding\n• Memory Usage Analysis: Check if 32MB limit caused service crash\n• Network Connectivity: Confirm frontend can reach GraphQL endpoint\n• Error Logs: Review GraphQL service logs for crash details\n• Configuration Impact: Assess impact of granularity change from 'minute' to 'second'"
                                }
                            ]
                        },
                        {
                            "type": "heading",
                            "attrs": {"level": 2},
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Business Impact"
                                }
                            ]
                        },
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "• User Impact: Customers cannot view product catalog\n• Service Availability: Product listing functionality unavailable\n• Customer Experience: Poor user experience with loading failures"
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": "Incident"
                },
                "labels": ["customer-reported", "ui-failure", "graphql-issue"]
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/issue",
                    headers=headers,
                    json=issue_data
                )
                
                if response.status_code == 201:
                    issue = response.json()
                    issue_key = issue.get("key")
                    print(f"✅ IR Ticket created successfully!")
                    print(f"🎫 Ticket ID: {issue_key}")
                    print(f"🔗 URL: {self.jira_url}/browse/{issue_key}")
                    return issue
                else:
                    print(f"❌ Failed to create ticket: {response.status_code}")
                    print(f"Response: {response.text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error creating ticket: {e}")
            return None

async def main():
    """Main function to create the IR ticket."""
    print("🚨 CREATING INCIDENT RESPONSE TICKET")
    print("=" * 50)
    
    try:
        creator = IRTicketCreator()
        
        # Get cloud ID
        cloud_id = await creator.get_cloud_id()
        if not cloud_id:
            print("❌ Could not get cloud ID. Exiting.")
            return
        
        # Create the ticket
        issue = await creator.create_issue(cloud_id)
        if issue:
            print(f"\n🎊 SUCCESS! IR Ticket created in {creator.jira_url}")
            print(f"📋 Ticket Details:")
            print(f"   Key: {issue.get('key')}")
            print(f"   ID: {issue.get('id')}")
            print(f"   URL: {creator.jira_url}/browse/{issue.get('key')}")
        else:
            print("❌ Failed to create IR ticket")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
