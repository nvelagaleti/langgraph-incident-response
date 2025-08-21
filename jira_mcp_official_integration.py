#!/usr/bin/env python3
"""
Official Jira MCP Integration using mcp-atlassian package.
Following the exact pattern specified by the user.
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

try:
    from mcp_atlassian import MCPClient
    MCP_ATLASSIAN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  mcp-atlassian not available: {e}")
    print("💡 Install with: pip install mcp-atlassian")
    MCP_ATLASSIAN_AVAILABLE = False

try:
    from langgraph.agent import Agent
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  LangGraph not available: {e}")
    print("💡 Install with: pip install langgraph")
    LANGGRAPH_AVAILABLE = False


class JiraMCPOfficialIntegration:
    """Official Jira MCP Integration using mcp-atlassian package."""
    
    def __init__(self):
        load_dotenv()
        self.mcp_client: Optional[MCPClient] = None
        self.agent: Optional[Agent] = None
        self.initialized = False
        
        # Jira configuration
        self.jira_url = "https://mcp.atlassian.com/v1/sse"
        self.oauth_token: Optional[str] = None
    
    async def initialize(self) -> bool:
        """Initialize Jira MCP integration using mcp-atlassian."""
        try:
            print("🔗 Initializing Official Jira MCP Integration...")
            
            # Check if mcp-atlassian is available
            if not MCP_ATLASSIAN_AVAILABLE:
                print("❌ mcp-atlassian package not available")
                return False
            
            # Get OAuth token from environment
            self.oauth_token = os.environ.get("JIRA_OAUTH_TOKEN")
            if not self.oauth_token:
                print("❌ JIRA_OAUTH_TOKEN not found in environment variables")
                print("💡 Make sure to set JIRA_OAUTH_TOKEN in your .env file")
                return False
            
            print(f"✅ Found JIRA_OAUTH_TOKEN: {self.oauth_token[:20]}...")
            
            # Initialize MCP client for Jira
            print("🔧 Initializing MCPClient...")
            self.mcp_client = MCPClient(
                url=self.jira_url,  # Official Atlassian MCP Server URL
                oauth_token=self.oauth_token  # Your OAuth token
            )
            
            print("✅ MCPClient initialized successfully!")
            
            # Initialize LangGraph agent if available
            if LANGGRAPH_AVAILABLE:
                print("🔧 Initializing LangGraph Agent...")
                self.agent = Agent(tools=self.mcp_client.tools)
                print("✅ LangGraph Agent initialized successfully!")
            
            self.initialized = True
            print("🎉 Official Jira MCP Integration initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Jira MCP integration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def list_tools(self) -> List[str]:
        """List all available Jira tools."""
        if not self.initialized or not self.mcp_client:
            print("❌ Integration not initialized")
            return []
        
        tools_list = list(self.mcp_client.tools.keys()) if hasattr(self.mcp_client.tools, 'keys') else []
        print(f"🛠️  Available Jira tools ({len(tools_list)}):")
        for i, tool_name in enumerate(tools_list, 1):
            print(f"   {i}. {tool_name}")
        
        return tools_list
    
    async def search_issues(self, jql: str = "project = 'IR' AND status = 'Open' ORDER BY created DESC", max_results: int = 5) -> List[Dict[str, Any]]:
        """Search Jira issues using JQL."""
        if not self.initialized or not self.mcp_client:
            print("❌ Integration not initialized")
            return []
        
        try:
            print(f"🔍 Searching Jira issues with JQL: {jql}")
            
            # Use the agent if available, otherwise use direct tool invocation
            if self.agent:
                response = await self.agent.run({
                    "tool": "search_issues",
                    "args": {
                        "jql": jql,
                        "max_results": max_results
                    }
                })
                print(f"✅ Agent response: {response}")
                return response if isinstance(response, list) else [response]
            else:
                # Direct tool invocation
                if hasattr(self.mcp_client, 'search_issues'):
                    result = await self.mcp_client.search_issues(jql=jql, max_results=max_results)
                    print(f"✅ Retrieved {len(result) if isinstance(result, list) else 1} issues")
                    return result if isinstance(result, list) else [result]
                else:
                    print("❌ search_issues tool not available")
                    return []
            
        except Exception as e:
            print(f"❌ Error searching issues: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get all Jira projects."""
        if not self.initialized or not self.mcp_client:
            print("❌ Integration not initialized")
            return []
        
        try:
            print("📋 Getting Jira projects...")
            
            # Use the agent if available, otherwise use direct tool invocation
            if self.agent:
                response = await self.agent.run({
                    "tool": "get_projects",
                    "args": {}
                })
                print(f"✅ Agent response: {response}")
                return response if isinstance(response, list) else [response]
            else:
                # Direct tool invocation
                if hasattr(self.mcp_client, 'get_projects'):
                    result = await self.mcp_client.get_projects()
                    print(f"✅ Retrieved {len(result) if isinstance(result, list) else 1} projects")
                    return result if isinstance(result, list) else [result]
                else:
                    print("❌ get_projects tool not available")
                    return []
            
        except Exception as e:
            print(f"❌ Error getting projects: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get a specific Jira issue by key."""
        if not self.initialized or not self.mcp_client:
            print("❌ Integration not initialized")
            return None
        
        try:
            print(f"📋 Getting Jira issue: {issue_key}")
            
            # Use the agent if available, otherwise use direct tool invocation
            if self.agent:
                response = await self.agent.run({
                    "tool": "get_issue",
                    "args": {
                        "issue_key": issue_key
                    }
                })
                print(f"✅ Agent response: {response}")
                return response
            else:
                # Direct tool invocation
                if hasattr(self.mcp_client, 'get_issue'):
                    result = await self.mcp_client.get_issue(issue_key=issue_key)
                    print(f"✅ Retrieved issue: {result.get('key', 'Unknown') if result else 'None'}")
                    return result
                else:
                    print("❌ get_issue tool not available")
                    return None
            
        except Exception as e:
            print(f"❌ Error getting issue: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Task") -> Optional[Dict[str, Any]]:
        """Create a new Jira issue."""
        if not self.initialized or not self.mcp_client:
            print("❌ Integration not initialized")
            return None
        
        try:
            print(f"📝 Creating Jira issue in project {project_key}...")
            
            # Use the agent if available, otherwise use direct tool invocation
            if self.agent:
                response = await self.agent.run({
                    "tool": "create_issue",
                    "args": {
                        "project_key": project_key,
                        "summary": summary,
                        "description": description,
                        "issue_type": issue_type
                    }
                })
                print(f"✅ Agent response: {response}")
                return response
            else:
                # Direct tool invocation
                if hasattr(self.mcp_client, 'create_issue'):
                    result = await self.mcp_client.create_issue(
                        project_key=project_key,
                        summary=summary,
                        description=description,
                        issue_type=issue_type
                    )
                    print(f"✅ Created issue: {result.get('key', 'Unknown') if result else 'None'}")
                    return result
                else:
                    print("❌ create_issue tool not available")
                    return None
            
        except Exception as e:
            print(f"❌ Error creating issue: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a Jira issue."""
        if not self.initialized or not self.mcp_client:
            print("❌ Integration not initialized")
            return None
        
        try:
            print(f"✏️  Updating Jira issue: {issue_key}")
            
            # Use the agent if available, otherwise use direct tool invocation
            if self.agent:
                response = await self.agent.run({
                    "tool": "update_issue",
                    "args": {
                        "issue_key": issue_key,
                        "fields": fields
                    }
                })
                print(f"✅ Agent response: {response}")
                return response
            else:
                # Direct tool invocation
                if hasattr(self.mcp_client, 'update_issue'):
                    result = await self.mcp_client.update_issue(issue_key=issue_key, fields=fields)
                    print(f"✅ Updated issue: {issue_key}")
                    return result
                else:
                    print("❌ update_issue tool not available")
                    return None
            
        except Exception as e:
            print(f"❌ Error updating issue: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def add_comment(self, issue_key: str, comment: str) -> Optional[Dict[str, Any]]:
        """Add a comment to a Jira issue."""
        if not self.initialized or not self.mcp_client:
            print("❌ Integration not initialized")
            return None
        
        try:
            print(f"💬 Adding comment to Jira issue: {issue_key}")
            
            # Use the agent if available, otherwise use direct tool invocation
            if self.agent:
                response = await self.agent.run({
                    "tool": "add_comment",
                    "args": {
                        "issue_key": issue_key,
                        "comment": comment
                    }
                })
                print(f"✅ Agent response: {response}")
                return response
            else:
                # Direct tool invocation
                if hasattr(self.mcp_client, 'add_comment'):
                    result = await self.mcp_client.add_comment(issue_key=issue_key, comment=comment)
                    print(f"✅ Added comment to issue: {result.get('id', 'Unknown') if result else 'None'}")
                    return result
                else:
                    print("❌ add_comment tool not available")
                    return None
            
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            import traceback
            traceback.print_exc()
            return None


async def main():
    """Main function to demonstrate Official Jira MCP integration."""
    print("🚀 Official Jira MCP Integration Demo")
    print("=" * 50)
    
    # Initialize integration
    jira_mcp = JiraMCPOfficialIntegration()
    
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
    issues = await jira_mcp.search_issues(
        jql="project = 'IR' AND status = 'Open' ORDER BY created DESC",
        max_results=5
    )
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
