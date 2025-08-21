#!/usr/bin/env python3
"""
Jira Integration Solution
Comprehensive solution for Jira integration with multiple approaches
"""

import os
import asyncio
import json
import requests
import base64
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

class JiraIntegrationSolution:
    """Comprehensive Jira integration solution."""
    
    def __init__(self):
        load_dotenv()
        self.jira_url = os.getenv("JIRA_URL")
        self.jira_token = os.getenv("JIRA_TOKEN")
        self.jira_email = os.getenv("JIRA_EMAIL")  # Add email for basic auth
        
    def test_jira_token_formats(self):
        """Test different Jira token formats."""
        print("🔍 Testing Jira Token Formats")
        print("=" * 50)
        
        if not self.jira_token:
            print("❌ No Jira token found")
            return False
            
        # Test different authentication methods
        auth_methods = [
            ("Bearer Token", {"Authorization": f"Bearer {self.jira_token}"}),
            ("Basic Auth (email:token)", {"Authorization": f"Basic {base64.b64encode(f'{self.jira_email}:{self.jira_token}'.encode()).decode()}"} if self.jira_email else None),
            ("Token Only", {"Authorization": f"token {self.jira_token}"}),
            ("X-Auth-Token", {"X-Auth-Token": self.jira_token}),
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
                user_url = f"{self.jira_url}/rest/api/3/myself"
                response = requests.get(user_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"✅ SUCCESS with {method_name}")
                    print(f"📄 User: {user_data.get('displayName', 'Unknown')}")
                    print(f"📄 Email: {user_data.get('emailAddress', 'Unknown')}")
                    return method_name, auth_header
                else:
                    print(f"❌ Failed: {response.status_code}")
                    print(f"📄 Response: {response.text[:100]}...")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
        return None, None
    
    def create_direct_jira_client(self, auth_method, auth_header):
        """Create a direct Jira API client."""
        class DirectJiraClient:
            def __init__(self, jira_url, headers):
                self.jira_url = jira_url
                self.headers = headers
                
            def get_projects(self):
                """Get all projects."""
                url = f"{self.jira_url}/rest/api/3/project"
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Failed to get projects: {response.status_code}")
                    
            def get_project(self, project_key):
                """Get specific project."""
                url = f"{self.jira_url}/rest/api/3/project/{project_key}"
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Failed to get project {project_key}: {response.status_code}")
                    
            def search_issues(self, jql, max_results=50):
                """Search issues."""
                url = f"{self.jira_url}/rest/api/3/search"
                data = {
                    "jql": jql,
                    "maxResults": max_results,
                    "fields": ["summary", "status", "created", "project"]
                }
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Failed to search issues: {response.status_code}")
                    
            def create_issue(self, project_key, summary, description, issue_type="Incident"):
                """Create an issue."""
                url = f"{self.jira_url}/rest/api/3/issue"
                data = {
                    "fields": {
                        "project": {"key": project_key},
                        "summary": summary,
                        "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]},
                        "issuetype": {"name": issue_type}
                    }
                }
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
                if response.status_code == 201:
                    return response.json()
                else:
                    raise Exception(f"Failed to create issue: {response.status_code}")
                    
            def add_comment(self, issue_key, comment):
                """Add comment to issue."""
                url = f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment"
                data = {
                    "body": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]}
                }
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
                if response.status_code == 201:
                    return response.json()
                else:
                    raise Exception(f"Failed to add comment: {response.status_code}")
        
        return DirectJiraClient(self.jira_url, auth_header)
    
    async def test_mcp_alternatives(self):
        """Test alternative MCP server configurations."""
        print(f"\n🔍 Testing MCP Server Alternatives")
        print("=" * 50)
        
        # Different MCP server URLs and configurations
        mcp_configs = [
            {
                "name": "Atlassian MCP (SSE)",
                "url": "https://mcp.atlassian.com/v1/sse",
                "headers": {
                    "Authorization": f"Bearer {self.jira_token}",
                    "Accept": "text/event-stream",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Atlassian MCP (Standard)",
                "url": "https://mcp.atlassian.com/v1",
                "headers": {
                    "Authorization": f"Bearer {self.jira_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Custom Jira MCP",
                "url": f"{self.jira_url}/rest/mcp",
                "headers": {
                    "Authorization": f"Bearer {self.jira_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            }
        ]
        
        for config in mcp_configs:
            print(f"\n🔍 Testing: {config['name']}")
            try:
                servers_config = {
                    "jira": {
                        "transport": "streamable_http",
                        "url": config["url"],
                        "headers": config["headers"]
                    }
                }
                
                client = MultiServerMCPClient(servers_config)
                tools = await client.get_tools()
                
                print(f"✅ SUCCESS: {len(tools)} tools loaded")
                return config
                
            except Exception as e:
                print(f"❌ Failed: {str(e)[:100]}...")
                
        return None
    
    def show_integration_recommendations(self, direct_auth_ok, mcp_config=None):
        """Show integration recommendations."""
        print(f"\n📋 Integration Recommendations")
        print("=" * 50)
        
        if direct_auth_ok:
            print(f"✅ Direct Jira API: WORKING")
            print(f"   - Use direct REST API calls")
            print(f"   - Full control over Jira operations")
            print(f"   - No MCP server dependency")
            print(f"   - Recommended for immediate use")
            
        if mcp_config:
            print(f"✅ MCP Server: WORKING")
            print(f"   - Use MCP protocol")
            print(f"   - Standardized tool interface")
            print(f"   - Better integration with LangGraph")
            print(f"   - Recommended for long-term use")
            
        if not direct_auth_ok and not mcp_config:
            print(f"❌ No working integration found")
            print(f"   - Check Jira token format")
            print(f"   - Verify Jira URL")
            print(f"   - Consider using email + API token")
            
        print(f"\n🎯 Recommended Approach:")
        if direct_auth_ok and mcp_config:
            print(f"   🔗 Hybrid: Use MCP for GitHub, Direct API for Jira")
        elif direct_auth_ok:
            print(f"   🔗 Hybrid: Use MCP for GitHub, Direct API for Jira")
        elif mcp_config:
            print(f"   🔗 Full MCP: Use MCP for both GitHub and Jira")
        else:
            print(f"   🔧 Fix authentication first")

async def main():
    """Main function."""
    print("🧪 Jira Integration Solution")
    print("=" * 60)
    
    solution = JiraIntegrationSolution()
    
    # Test 1: Direct API authentication
    print("🔍 Step 1: Testing Direct Jira API Authentication")
    auth_method, auth_header = solution.test_jira_token_formats()
    
    direct_auth_ok = auth_method is not None
    
    # Test 2: MCP alternatives
    print(f"\n🔍 Step 2: Testing MCP Server Alternatives")
    mcp_config = await solution.test_mcp_alternatives()
    
    # Show recommendations
    solution.show_integration_recommendations(direct_auth_ok, mcp_config)
    
    # Test 3: Create working client
    if direct_auth_ok:
        print(f"\n🔍 Step 3: Testing Direct Jira Client")
        client = solution.create_direct_jira_client(auth_method, auth_header)
        
        try:
            # Test getting projects
            projects = client.get_projects()
            print(f"✅ Direct client working")
            print(f"📄 Found {len(projects)} projects")
            
            # Show project keys
            project_keys = [proj.get('key', '') for proj in projects if proj.get('key')]
            print(f"📋 Project Keys: {', '.join(project_keys[:10])}")
            
        except Exception as e:
            print(f"❌ Direct client test failed: {e}")
    
    # Final summary
    print(f"\n🎉 Integration Test Results:")
    print("=" * 50)
    print(f"✅ Direct Jira API: {'PASS' if direct_auth_ok else 'FAIL'}")
    print(f"✅ MCP Server: {'PASS' if mcp_config else 'FAIL'}")
    
    if direct_auth_ok or mcp_config:
        print(f"\n🎊 SUCCESS! Jira integration is possible!")
        print(f"🚀 Ready to integrate with incident response system!")
    else:
        print(f"\n⚠️  Authentication issues need to be resolved")
        print(f"💡 Check your Jira token and URL configuration")

if __name__ == "__main__":
    asyncio.run(main())
