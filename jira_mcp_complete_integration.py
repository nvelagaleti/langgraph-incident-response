#!/usr/bin/env python3
"""
Complete Jira MCP Integration using direct API with MCP pattern.
This follows the same pattern as our successful GitHub MCP integration
but uses the direct Jira API since the Atlassian MCP server has authentication issues.
"""

import asyncio
import os
import json
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from token_manager import TokenManager

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.tools import load_mcp_tools
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  MCP adapters not available: {e}")
    print("💡 Install with: pip install langchain-mcp-adapters")
    MCP_AVAILABLE = False

try:
    from langgraph.agent import Agent
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  LangGraph not available: {e}")
    print("💡 Install with: pip install langgraph")
    LANGGRAPH_AVAILABLE = False


class JiraMCPCompleteIntegration:
    """Complete Jira MCP Integration using direct API with MCP pattern."""
    
    def __init__(self):
        # Don't load dotenv or create token manager here - do it async in initialize()
        self.token_manager: Optional[TokenManager] = None
        self.client: Optional[MultiServerMCPClient] = None
        self.agent: Optional[Agent] = None
        self.tools: Dict[str, Any] = {}
        self.initialized = False
        
        # Jira configuration
        self.jira_url = os.getenv("JIRA_URL", "https://mailtosimha.atlassian.net")
        self.access_token: Optional[str] = None
        self.cloud_id: Optional[str] = os.getenv("JIRA_CLOUD_ID")
        
        # Define available tools (simulating MCP tools)
        self.available_tools = {
            "get_projects": {
                "name": "get_projects",
                "description": "Get all Jira projects accessible to the user",
                "parameters": {}
            },
            "search_issues": {
                "name": "search_issues", 
                "description": "Search Jira issues using JQL",
                "parameters": {
                    "jql": "string",
                    "maxResults": "integer"
                }
            },
            "get_issue": {
                "name": "get_issue",
                "description": "Get a specific Jira issue by key",
                "parameters": {
                    "issueKey": "string"
                }
            },
            "create_issue": {
                "name": "create_issue",
                "description": "Create a new Jira issue",
                "parameters": {
                    "project": "object",
                    "summary": "string", 
                    "description": "string",
                    "issuetype": "object"
                }
            },
            "update_issue": {
                "name": "update_issue",
                "description": "Update a Jira issue",
                "parameters": {
                    "issueKey": "string",
                    "fields": "object"
                }
            },
            "add_comment": {
                "name": "add_comment",
                "description": "Add a comment to a Jira issue",
                "parameters": {
                    "issueKey": "string",
                    "body": "string"
                }
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize Jira MCP integration using direct API with MCP pattern."""
        try:
            print("🔗 Initializing Complete Jira MCP Integration...")
            
            # Load environment variables and create token manager asynchronously
            await asyncio.to_thread(load_dotenv)
            self.token_manager = TokenManager()
            await self.token_manager.initialize()
            
            # Ensure we have a valid token
            self.access_token = await self.token_manager.ensure_valid_token()
            if not self.access_token:
                print("❌ Failed to obtain valid access token")
                return False
            
            print(f"✅ Access token obtained: {self.access_token[:20]}...")
            
            # Get cloud ID (required for API calls)
            self.cloud_id = await self._get_cloud_id()
            if not self.cloud_id:
                print("❌ Failed to get cloud ID")
                return False
            
            print(f"✅ Cloud ID obtained: {self.cloud_id}")
            
            # Initialize tools
            for tool_name, tool_info in self.available_tools.items():
                self.tools[tool_name] = tool_info
            
            # Try to initialize MCP client for consistency (optional)
            if MCP_AVAILABLE:
                try:
                    # Configure a mock MCP server for consistency
                    servers_config = {
                        "jira_direct": {
                            "transport": "streamable_http",
                            "url": "https://api.atlassian.com",  # Mock URL
                            "headers": {
                                "Authorization": f"Bearer {self.access_token}",
                                "Content-Type": "application/json",
                                "User-Agent": "LangGraph-Incident-Response/1.0"
                            }
                        }
                    }
                    
                    self.client = MultiServerMCPClient(servers_config)
                    print("✅ MCP client initialized for consistency")
                except Exception as e:
                    print(f"⚠️  MCP client initialization failed (continuing with direct API): {e}")
            
            # Initialize LangGraph agent if available
            if LANGGRAPH_AVAILABLE and self.client:
                try:
                    # Create mock tools for the agent
                    mock_tools = []
                    for tool_name, tool_info in self.available_tools.items():
                        # Create a mock tool object
                        mock_tool = type('MockTool', (), {
                            'name': tool_name,
                            'description': tool_info['description'],
                            'ainvoke': lambda self, args, tool_name=tool_name: self._invoke_tool_direct(tool_name, args)
                        })()
                        mock_tools.append(mock_tool)
                    
                    self.agent = Agent(tools=mock_tools)
                    print("✅ LangGraph Agent initialized")
                except Exception as e:
                    print(f"⚠️  LangGraph Agent initialization failed: {e}")
            
            self.initialized = True
            print("🎉 Complete Jira MCP Integration initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Jira MCP integration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _get_cloud_id(self) -> Optional[str]:
        """Get the cloud ID for the Jira instance."""
        # First try to use environment variable
        if self.cloud_id:
            print(f"✅ Using cloud ID from environment: {self.cloud_id}")
            return self.cloud_id
        
        # Fallback to API call
        try:
            print("🔍 Getting cloud ID from API...")
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.atlassian.com/oauth/token/accessible-resources",
                    headers=headers
                )
                response.raise_for_status()
                
                resources = response.json()
                if resources:
                    # Use the first resource (assuming single Jira instance)
                    cloud_id = resources[0]["id"]
                    print(f"✅ Retrieved cloud ID from API: {cloud_id}")
                    return cloud_id
                
                print("❌ No resources found in API response")
                return None
                
        except Exception as e:
            print(f"❌ Error getting cloud ID from API: {e}")
            return None
    
    async def _invoke_tool_direct(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Invoke a Jira tool directly using the API."""
        if tool_name == "get_projects":
            return await self._get_projects()
        elif tool_name == "search_issues":
            return await self._search_issues(
                arguments.get("jql", "project in (IR)"),
                arguments.get("maxResults", 50)
            )
        elif tool_name == "get_issue":
            return await self._get_issue(arguments.get("issueKey"))
        elif tool_name == "create_issue":
            return await self._create_issue(
                arguments.get("project", {}).get("key"),
                arguments.get("summary"),
                arguments.get("description"),
                arguments.get("issuetype", {}).get("name", "Task")
            )
        elif tool_name == "update_issue":
            return await self._update_issue(
                arguments.get("issueKey"),
                arguments.get("fields", {})
            )
        elif tool_name == "add_comment":
            return await self._add_comment(
                arguments.get("issueKey"),
                arguments.get("body")
            )
        else:
            print(f"❌ Tool '{tool_name}' not implemented")
            return None
    
    async def list_tools(self) -> List[str]:
        """List all available Jira tools."""
        if not self.initialized:
            print("❌ Integration not initialized")
            return []
        
        tools_list = list(self.tools.keys())
        print(f"🛠️  Available Jira tools ({len(tools_list)}):")
        for i, tool_name in enumerate(tools_list, 1):
            tool = self.tools[tool_name]
            print(f"   {i}. {tool['name']}: {tool['description']}")
        
        return tools_list
    
    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Invoke a Jira tool with arguments."""
        return await self._invoke_tool_direct(tool_name, arguments)
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get all Jira projects."""
        return await self.invoke_tool("get_projects", {})
    
    async def _get_projects(self) -> List[Dict[str, Any]]:
        """Get all Jira projects using direct API."""
        try:
            print("📋 Getting Jira projects...")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            }
            
            url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/3/project"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                projects = response.json()
                print(f"✅ Retrieved {len(projects)} projects")
                return projects
                
        except Exception as e:
            print(f"❌ Error getting projects: {e}")
            return []
    
    async def search_issues(self, jql: str = "project in (IR)", max_results: int = 50) -> List[Dict[str, Any]]:
        """Search Jira issues using JQL."""
        return await self.invoke_tool("search_issues", {"jql": jql, "maxResults": max_results})
    
    async def _search_issues(self, jql: str, max_results: int) -> List[Dict[str, Any]]:
        """Search Jira issues using direct API."""
        try:
            print(f"🔍 Searching Jira issues with JQL: {jql}")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/3/search"
            
            data = {
                "jql": jql,
                "maxResults": max_results,
                "fields": ["summary", "description", "priority", "assignee", "reporter", "labels", "environment"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                issues = result.get("issues", [])
                print(f"✅ Retrieved {len(issues)} issues")
                return issues
                
        except Exception as e:
            print(f"❌ Error searching issues: {e}")
            return []
    
    async def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get a specific Jira issue by key."""
        return await self.invoke_tool("get_issue", {"issueKey": issue_key})
    
    async def _get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get a specific Jira issue using direct API."""
        try:
            print(f"📋 Getting Jira issue: {issue_key}")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            }
            
            url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/3/issue/{issue_key}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                issue = response.json()
                print(f"✅ Retrieved issue: {issue.get('key', 'Unknown')}")
                return issue
                
        except Exception as e:
            print(f"❌ Error getting issue: {e}")
            return None
    
    async def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Task") -> Optional[Dict[str, Any]]:
        """Create a new Jira issue."""
        return await self.invoke_tool("create_issue", {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type}
        })
    
    async def _create_issue(self, project_key: str, summary: str, description: str, issue_type: str) -> Optional[Dict[str, Any]]:
        """Create a new Jira issue using direct API."""
        try:
            print(f"📝 Creating Jira issue in project {project_key}...")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/3/issue"
            
            data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]},
                    "issuetype": {"name": issue_type}
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                issue = response.json()
                print(f"✅ Created issue: {issue.get('key', 'Unknown')}")
                return issue
                
        except Exception as e:
            print(f"❌ Error creating issue: {e}")
            return None
    
    async def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a Jira issue."""
        return await self.invoke_tool("update_issue", {"issueKey": issue_key, "fields": fields})
    
    async def _update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a Jira issue using direct API."""
        try:
            print(f"✏️  Updating Jira issue: {issue_key}")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/3/issue/{issue_key}"
            
            data = {"fields": fields}
            
            async with httpx.AsyncClient() as client:
                response = await client.put(url, headers=headers, json=data)
                response.raise_for_status()
                
                print(f"✅ Updated issue: {issue_key}")
                return {"key": issue_key, "updated": True}
                
        except Exception as e:
            print(f"❌ Error updating issue: {e}")
            return None
    
    async def add_comment(self, issue_key: str, comment: str) -> Optional[Dict[str, Any]]:
        """Add a comment to a Jira issue."""
        return await self.invoke_tool("add_comment", {"issueKey": issue_key, "body": comment})
    
    async def _add_comment(self, issue_key: str, comment: str) -> Optional[Dict[str, Any]]:
        """Add a comment to a Jira issue using direct API."""
        try:
            print(f"💬 Adding comment to Jira issue: {issue_key}")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            url = f"https://api.atlassian.com/ex/jira/{self.cloud_id}/rest/api/3/issue/{issue_key}/comment"
            
            data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                print(f"✅ Added comment to issue: {result.get('id', 'Unknown')}")
                return result
                
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            return None


async def main():
    """Main function to demonstrate Complete Jira MCP integration."""
    print("🚀 Complete Jira MCP Integration Demo")
    print("=" * 50)
    
    # Initialize integration
    jira_mcp = JiraMCPCompleteIntegration()
    
    # Initialize
    if not await jira_mcp.initialize():
        print("❌ Failed to initialize Jira MCP integration")
        return
    
    print("\n" + "=" * 50)
    
    # List available tools
    print("\n📋 Available Tools:")
    await jira_mcp.list_tools()
    
    print("\n" + "=" * 50)
    
    # Get projects
    print("\n📋 Getting Projects:")
    projects = await jira_mcp.get_projects()
    if projects:
        print(f"✅ Found {len(projects)} projects")
        for project in projects[:3]:  # Show first 3
            print(f"   - {project.get('key', 'N/A')}: {project.get('name', 'N/A')}")
    else:
        print("❌ No projects found")
    
    print("\n" + "=" * 50)
    
    # Search issues
    print("\n🔍 Searching Issues:")
    issues = await jira_mcp.search_issues(jql="project in (IR)", max_results=5)
    if issues:
        print(f"✅ Found {len(issues)} issues")
        for issue in issues[:3]:  # Show first 3
            print(f"   - {issue.get('key', 'N/A')}: {issue.get('fields', {}).get('summary', 'N/A')}")
    else:
        print("❌ No issues found")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
