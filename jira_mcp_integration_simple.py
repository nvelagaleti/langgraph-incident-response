#!/usr/bin/env python3
"""
Simple Jira MCP Integration using the official Atlassian MCP server.
Using the exact format specified by the user.
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

try:
    from langchain_mcp import MCPToolkit
    LANGCHAIN_MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  LangChain MCP not available: {e}")
    print("💡 Install with: pip install langchain-mcp")
    LANGCHAIN_MCP_AVAILABLE = False


class JiraMCPSimpleIntegration:
    """Simple Jira MCP Integration using the official Atlassian MCP server."""
    
    def __init__(self):
        load_dotenv()
        self.toolkit: Optional[MCPToolkit] = None
        self.tools: Dict[str, Any] = {}
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize Jira MCP integration using the specified format."""
        try:
            print("🔗 Initializing Jira MCP Integration...")
            
            # Check if JIRA_OAUTH_TOKEN is available
            jira_token = os.environ.get("JIRA_OAUTH_TOKEN")
            if not jira_token:
                print("❌ JIRA_OAUTH_TOKEN not found in environment variables")
                print("💡 Make sure to set JIRA_OAUTH_TOKEN in your .env file")
                return False
            
            print(f"✅ Found JIRA_OAUTH_TOKEN: {jira_token[:20]}...")
            
            if not LANGCHAIN_MCP_AVAILABLE:
                print("❌ LangChain MCP not available")
                return False
            
            # Initialize using the exact format specified
            print("🔧 Initializing MCPToolkit with specified format...")
            self.toolkit = MCPToolkit.from_mcp(
                url="https://mcp.atlassian.com/v1/sse",
                auth_mode="oauth",
                oauth_token=os.environ["JIRA_OAUTH_TOKEN"]
            )
            
            # Get tools from toolkit
            toolkit_tools = self.toolkit.tools
            print(f"📋 Loaded {len(toolkit_tools)} tools from MCPToolkit")
            
            # Store tools
            for tool in toolkit_tools:
                self.tools[tool.name] = tool
            
            self.initialized = True
            print("🎉 Jira MCP Integration initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Jira MCP integration: {e}")
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
            result = await tool.ainvoke({})
            
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
            result = await tool.ainvoke(args)
            
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
            result = await tool.ainvoke(args)
            
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
            result = await tool.ainvoke(args)
            
            print(f"✅ Retrieved issue: {result.get('key', 'Unknown')}")
            return result
            
        except Exception as e:
            print(f"❌ Error getting issue: {e}")
            return None


async def main():
    """Main function to demonstrate Jira MCP integration."""
    print("🚀 Jira MCP Integration Demo (Simple)")
    print("=" * 50)
    
    # Initialize integration
    jira_mcp = JiraMCPSimpleIntegration()
    
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
