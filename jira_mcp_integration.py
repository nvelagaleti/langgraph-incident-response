#!/usr/bin/env python3
"""
Jira MCP Integration using the official Atlassian MCP server.
Follows the same pattern as our GitHub MCP integration.
"""

import asyncio
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import the token manager we created earlier
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
    from langchain_mcp import MCPToolkit
    LANGCHAIN_MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  LangChain MCP not available: {e}")
    print("💡 Install with: pip install langchain-mcp")
    LANGCHAIN_MCP_AVAILABLE = False


class JiraMCPIntegration:
    """Jira MCP Integration using the official Atlassian MCP server."""
    
    def __init__(self):
        load_dotenv()
        self.token_manager = TokenManager()
        self.client: Optional[MultiServerMCPClient] = None
        self.toolkit: Optional[MCPToolkit] = None
        self.tools: Dict[str, Any] = {}
        self.initialized = False
        
        # Atlassian MCP server configuration
        self.atlassian_mcp_url = "https://mcp.atlassian.com/v1/sse"
        self.access_token: Optional[str] = None
    
    async def initialize(self) -> bool:
        """Initialize Jira MCP integration."""
        try:
            print("🔗 Initializing Jira MCP Integration...")
            
            # Ensure we have a valid token
            self.access_token = await self.token_manager.ensure_valid_token()
            if not self.access_token:
                print("❌ Failed to obtain valid access token")
                return False
            
            print(f"✅ Access token obtained: {self.access_token[:20]}...")
            
            # Try both approaches: MultiServerMCPClient and MCPToolkit
            success = False
            
            # Approach 1: MultiServerMCPClient (like GitHub)
            if MCP_AVAILABLE:
                success = await self._initialize_mcp_client()
                if success:
                    print("✅ Initialized with MultiServerMCPClient")
            
            # Approach 2: MCPToolkit (LangChain approach)
            if not success and LANGCHAIN_MCP_AVAILABLE:
                success = await self._initialize_mcp_toolkit()
                if success:
                    print("✅ Initialized with MCPToolkit")
            
            if success:
                self.initialized = True
                print("🎉 Jira MCP Integration initialized successfully!")
                return True
            else:
                print("❌ Failed to initialize with any MCP approach")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing Jira MCP integration: {e}")
            return False
    
    async def _initialize_mcp_client(self) -> bool:
        """Initialize using MultiServerMCPClient approach."""
        try:
            print("🔧 Initializing MultiServerMCPClient...")
            
            # Configure the Atlassian MCP server
            servers_config = {
                "atlassian": {
                    "transport": "streamable_http",
                    "url": self.atlassian_mcp_url,
                    "headers": {
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json",
                        "User-Agent": "LangGraph-Incident-Response/1.0"
                    }
                }
            }
            
            # Initialize the client
            self.client = MultiServerMCPClient(servers_config)
            
            # Load tools
            tools_list = await self.client.get_tools()
            print(f"📋 Loaded {len(tools_list)} tools from Atlassian MCP server")
            
            # Store tools
            for tool in tools_list:
                self.tools[tool.name] = tool
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing MultiServerMCPClient: {e}")
            return False
    
    async def _initialize_mcp_toolkit(self) -> bool:
        """Initialize using MCPToolkit approach."""
        try:
            print("🔧 Initializing MCPToolkit...")
            
            # Initialize MCPToolkit with Atlassian MCP server
            self.toolkit = MCPToolkit.from_mcp(
                url=self.atlassian_mcp_url,
                auth_mode="oauth",
                oauth_token=self.access_token
            )
            
            # Get tools from toolkit
            toolkit_tools = self.toolkit.tools
            print(f"📋 Loaded {len(toolkit_tools)} tools from MCPToolkit")
            
            # Store tools
            for tool in toolkit_tools:
                self.tools[tool.name] = tool
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing MCPToolkit: {e}")
            return False
    
    async def list_tools(self) -> List[str]:
        """List all available Jira tools."""
        if not self.initialized:
            print("❌ Integration not initialized")
            return []
        
        tools_list = list(self.tools.keys())
        print(f"🛠️  Available Jira tools ({len(tools_list)}):")
        for i, tool_name in enumerate(tools_list, 1):
            tool = self.tools[tool_name]
            description = getattr(tool, 'description', 'No description')
            print(f"   {i}. {tool_name}: {description}")
        
        return tools_list
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get all Jira projects."""
        if not self.initialized:
            print("❌ Integration not initialized")
            return []
        
        try:
            print("📋 Getting Jira projects...")
            
            # Try to find a project-related tool
            project_tools = [name for name in self.tools.keys() if 'project' in name.lower()]
            
            if not project_tools:
                print("⚠️  No project-related tools found")
                return []
            
            # Use the first project tool available
            tool_name = project_tools[0]
            tool = self.tools[tool_name]
            
            print(f"🔧 Using tool: {tool_name}")
            
            # Invoke the tool
            if self.client:
                result = await self.client.invoke_tool(tool_name, {})
            elif self.toolkit:
                result = await tool.ainvoke({})
            else:
                print("❌ No client or toolkit available")
                return []
            
            print(f"✅ Retrieved {len(result) if isinstance(result, list) else 1} project(s)")
            return result if isinstance(result, list) else [result]
            
        except Exception as e:
            print(f"❌ Error getting projects: {e}")
            return []
    
    async def search_issues(self, jql: str = "project in projectsWhereUserHasPermission()", max_results: int = 50) -> List[Dict[str, Any]]:
        """Search Jira issues using JQL."""
        if not self.initialized:
            print("❌ Integration not initialized")
            return []
        
        try:
            print(f"🔍 Searching Jira issues with JQL: {jql}")
            
            # Try to find a search-related tool
            search_tools = [name for name in self.tools.keys() if 'search' in name.lower() or 'issue' in name.lower()]
            
            if not search_tools:
                print("⚠️  No search-related tools found")
                return []
            
            # Use the first search tool available
            tool_name = search_tools[0]
            tool = self.tools[tool_name]
            
            print(f"🔧 Using tool: {tool_name}")
            
            # Prepare arguments
            args = {
                "jql": jql,
                "maxResults": max_results
            }
            
            # Invoke the tool
            if self.client:
                result = await self.client.invoke_tool(tool_name, args)
            elif self.toolkit:
                result = await tool.ainvoke(args)
            else:
                print("❌ No client or toolkit available")
                return []
            
            print(f"✅ Retrieved {len(result.get('issues', []))} issues")
            return result.get('issues', [])
            
        except Exception as e:
            print(f"❌ Error searching issues: {e}")
            return []
    
    async def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Task") -> Optional[Dict[str, Any]]:
        """Create a new Jira issue."""
        if not self.initialized:
            print("❌ Integration not initialized")
            return None
        
        try:
            print(f"📝 Creating Jira issue in project {project_key}...")
            
            # Try to find a create-related tool
            create_tools = [name for name in self.tools.keys() if 'create' in name.lower() or 'issue' in name.lower()]
            
            if not create_tools:
                print("⚠️  No create-related tools found")
                return None
            
            # Use the first create tool available
            tool_name = create_tools[0]
            tool = self.tools[tool_name]
            
            print(f"🔧 Using tool: {tool_name}")
            
            # Prepare arguments
            args = {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type}
            }
            
            # Invoke the tool
            if self.client:
                result = await self.client.invoke_tool(tool_name, args)
            elif self.toolkit:
                result = await tool.ainvoke(args)
            else:
                print("❌ No client or toolkit available")
                return None
            
            print(f"✅ Created issue: {result.get('key', 'Unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Error creating issue: {e}")
            return None
    
    async def get_issue(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Get a specific Jira issue by key."""
        if not self.initialized:
            print("❌ Integration not initialized")
            return None
        
        try:
            print(f"📋 Getting Jira issue: {issue_key}")
            
            # Try to find a get-related tool
            get_tools = [name for name in self.tools.keys() if 'get' in name.lower() or 'issue' in name.lower()]
            
            if not get_tools:
                print("⚠️  No get-related tools found")
                return None
            
            # Use the first get tool available
            tool_name = get_tools[0]
            tool = self.tools[tool_name]
            
            print(f"🔧 Using tool: {tool_name}")
            
            # Prepare arguments
            args = {"issueKey": issue_key}
            
            # Invoke the tool
            if self.client:
                result = await self.client.invoke_tool(tool_name, args)
            elif self.toolkit:
                result = await tool.ainvoke(args)
            else:
                print("❌ No client or toolkit available")
                return None
            
            print(f"✅ Retrieved issue: {result.get('key', 'Unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Error getting issue: {e}")
            return None
    
    async def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a Jira issue."""
        if not self.initialized:
            print("❌ Integration not initialized")
            return None
        
        try:
            print(f"✏️  Updating Jira issue: {issue_key}")
            
            # Try to find an update-related tool
            update_tools = [name for name in self.tools.keys() if 'update' in name.lower() or 'edit' in name.lower()]
            
            if not update_tools:
                print("⚠️  No update-related tools found")
                return None
            
            # Use the first update tool available
            tool_name = update_tools[0]
            tool = self.tools[tool_name]
            
            print(f"🔧 Using tool: {tool_name}")
            
            # Prepare arguments
            args = {
                "issueKey": issue_key,
                "fields": fields
            }
            
            # Invoke the tool
            if self.client:
                result = await self.client.invoke_tool(tool_name, args)
            elif self.toolkit:
                result = await tool.ainvoke(args)
            else:
                print("❌ No client or toolkit available")
                return None
            
            print(f"✅ Updated issue: {result.get('key', 'Unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Error updating issue: {e}")
            return None
    
    async def add_comment(self, issue_key: str, comment: str) -> Optional[Dict[str, Any]]:
        """Add a comment to a Jira issue."""
        if not self.initialized:
            print("❌ Integration not initialized")
            return None
        
        try:
            print(f"💬 Adding comment to Jira issue: {issue_key}")
            
            # Try to find a comment-related tool
            comment_tools = [name for name in self.tools.keys() if 'comment' in name.lower()]
            
            if not comment_tools:
                print("⚠️  No comment-related tools found")
                return None
            
            # Use the first comment tool available
            tool_name = comment_tools[0]
            tool = self.tools[tool_name]
            
            print(f"🔧 Using tool: {tool_name}")
            
            # Prepare arguments
            args = {
                "issueKey": issue_key,
                "body": comment
            }
            
            # Invoke the tool
            if self.client:
                result = await self.client.invoke_tool(tool_name, args)
            elif self.toolkit:
                result = await tool.ainvoke(args)
            else:
                print("❌ No client or toolkit available")
                return None
            
            print(f"✅ Added comment to issue: {result.get('id', 'Unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            return None


async def main():
    """Main function to demonstrate Jira MCP integration."""
    print("🚀 Jira MCP Integration Demo")
    print("=" * 50)
    
    # Initialize integration
    jira_mcp = JiraMCPIntegration()
    
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
    issues = await jira_mcp.search_issues(max_results=5)
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
