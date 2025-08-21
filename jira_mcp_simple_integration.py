#!/usr/bin/env python3
"""
Simple Jira MCP Integration
Uses MCP toolkit directly without LangGraph agent dependency
"""

import os
import asyncio
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from token_manager import TokenManager

# Import MCP components
try:
    from langchain_mcp import MCPToolkit
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  MCP components not available: {e}")
    print("💡 Install with: pip install langchain-mcp")
    MCP_AVAILABLE = False

class JiraMCPSimpleIntegration:
    """Simple Jira MCP integration using MCP toolkit directly."""
    
    def __init__(self):
        load_dotenv()
        self.token_manager = TokenManager()
        self.jira_toolkit = None
        
    async def initialize(self):
        """Initialize the MCP toolkit with token management."""
        print("🚀 Initializing Jira MCP Simple Integration")
        print("=" * 50)
        
        if not MCP_AVAILABLE:
            print("❌ MCP components not available")
            return False
        
        # Ensure we have a valid token
        token = await self.token_manager.ensure_valid_token()
        if not token:
            print("❌ Failed to obtain valid token")
            return False
        
        print(f"✅ Token validated successfully")
        
        try:
            # Initialize MCP toolkit exactly as in the user's example
            print("🔗 Initializing MCP Toolkit...")
            self.jira_toolkit = MCPToolkit.from_mcp(
                url="https://mcp.atlassian.com/v1/sse",
                auth_mode="oauth",
                oauth_token=token
            )
            
            print(f"✅ MCP Toolkit initialized successfully")
            print(f"📊 Available tools: {len(self.jira_toolkit.tools)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing MCP toolkit: {e}")
            return False
    
    def list_tools(self):
        """List all available tools."""
        if not self.jira_toolkit:
            print("❌ MCP toolkit not initialized")
            return
        
        print(f"\n🔧 Available Jira MCP Tools ({len(self.jira_toolkit.tools)} total)")
        print("=" * 60)
        
        for i, tool in enumerate(self.jira_toolkit.tools, 1):
            print(f"\n{i}. Tool: {tool.name}")
            if hasattr(tool, 'description'):
                print(f"   📝 Description: {tool.description}")
            print(f"   🔧 Type: {type(tool).__name__}")
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get Jira projects using MCP tools."""
        print(f"\n🔍 Getting Jira Projects via MCP")
        print("-" * 40)
        
        if not self.jira_toolkit:
            print("❌ MCP toolkit not initialized")
            return []
        
        try:
            # Find the get_projects tool
            get_projects_tool = None
            for tool in self.jira_toolkit.tools:
                if tool.name == 'get_projects':
                    get_projects_tool = tool
                    break
            
            if not get_projects_tool:
                print("❌ get_projects tool not found")
                print("📋 Available tools:")
                for tool in self.jira_toolkit.tools:
                    print(f"   - {tool.name}")
                return []
            
            print("✅ Found get_projects tool")
            
            # Invoke the tool
            print("🔄 Fetching projects...")
            result = await get_projects_tool.ainvoke({})
            
            # Parse result
            if isinstance(result, str):
                try:
                    projects_data = json.loads(result)
                except json.JSONDecodeError:
                    print("❌ Failed to parse projects data")
                    return []
            else:
                projects_data = result
            
            # Extract projects list
            if isinstance(projects_data, list):
                projects = projects_data
            elif isinstance(projects_data, dict) and 'values' in projects_data:
                projects = projects_data['values']
            else:
                print(f"❌ Unexpected projects data format: {type(projects_data)}")
                return []
            
            print(f"✅ Retrieved {len(projects)} projects via MCP")
            return projects
            
        except Exception as e:
            print(f"❌ Error getting projects via MCP: {e}")
            return []
    
    async def search_issues(self, jql: str = "ORDER BY created DESC", max_results: int = 5) -> List[Dict[str, Any]]:
        """Search issues using MCP tools."""
        print(f"\n🔍 Searching Issues via MCP")
        print("-" * 40)
        
        if not self.jira_toolkit:
            print("❌ MCP toolkit not initialized")
            return []
        
        try:
            # Find the search_issues tool
            search_issues_tool = None
            for tool in self.jira_toolkit.tools:
                if tool.name == 'search_issues':
                    search_issues_tool = tool
                    break
            
            if not search_issues_tool:
                print("❌ search_issues tool not found")
                return []
            
            print("✅ Found search_issues tool")
            
            # Prepare search parameters
            search_params = {
                "jql": jql,
                "max_results": max_results
            }
            
            print(f"🔄 Searching with JQL: {jql}")
            
            # Invoke the tool
            result = await search_issues_tool.ainvoke(search_params)
            
            # Parse result
            if isinstance(result, str):
                try:
                    issues_data = json.loads(result)
                except json.JSONDecodeError:
                    print("❌ Failed to parse issues data")
                    return []
            else:
                issues_data = result
            
            # Extract issues list
            if isinstance(issues_data, list):
                issues = issues_data
            elif isinstance(issues_data, dict) and 'issues' in issues_data:
                issues = issues_data['issues']
            else:
                print(f"❌ Unexpected issues data format: {type(issues_data)}")
                return []
            
            print(f"✅ Found {len(issues)} issues via MCP")
            return issues
            
        except Exception as e:
            print(f"❌ Error searching issues: {e}")
            return []
    
    def display_projects(self, projects: List[Dict[str, Any]]):
        """Display projects in a formatted way."""
        print(f"\n📋 Jira Projects via MCP ({len(projects)} total)")
        print("=" * 60)
        
        if not projects:
            print("❌ No projects found")
            return
        
        for i, project in enumerate(projects, 1):
            print(f"\n{i}. Project Details:")
            print(f"   🔑 Key: {project.get('key', 'N/A')}")
            print(f"   📝 Name: {project.get('name', 'N/A')}")
            print(f"   🆔 ID: {project.get('id', 'N/A')}")
            print(f"   📊 Project Type: {project.get('projectTypeKey', 'N/A')}")
            
            # Additional details if available
            if 'lead' in project:
                print(f"   👤 Lead: {project['lead'].get('displayName', 'N/A')}")
            
            if 'simplified' in project:
                print(f"   ⚡ Simplified: {project['simplified']}")
    
    def display_issues(self, issues: List[Dict[str, Any]]):
        """Display issues in a formatted way."""
        print(f"\n🎫 Jira Issues via MCP ({len(issues)} total)")
        print("=" * 60)
        
        if not issues:
            print("❌ No issues found")
            return
        
        for i, issue in enumerate(issues, 1):
            print(f"\n{i}. Issue Details:")
            print(f"   🔑 Key: {issue.get('key', 'N/A')}")
            print(f"   📝 Summary: {issue.get('fields', {}).get('summary', 'N/A')}")
            print(f"   🆔 ID: {issue.get('id', 'N/A')}")
            print(f"   📊 Status: {issue.get('fields', {}).get('status', {}).get('name', 'N/A')}")
            print(f"   🏷️  Type: {issue.get('fields', {}).get('issuetype', {}).get('name', 'N/A')}")

async def main():
    """Main function demonstrating the simple MCP integration."""
    print("🚀 Jira MCP Simple Integration Demo")
    print("=" * 60)
    
    # Initialize integration
    integration = JiraMCPSimpleIntegration()
    
    # Initialize connection
    success = await integration.initialize()
    if not success:
        print("❌ Failed to initialize integration")
        return
    
    try:
        # List available tools
        integration.list_tools()
        
        # Get projects using MCP
        projects = await integration.get_projects()
        
        if projects:
            # Display projects
            integration.display_projects(projects)
            
            # Search for recent issues
            issues = await integration.search_issues("ORDER BY created DESC", max_results=5)
            
            if issues:
                # Display issues
                integration.display_issues(issues)
            
            print(f"\n🎉 Successfully retrieved {len(projects)} projects and {len(issues)} issues via MCP!")
            
        else:
            print("❌ No projects found via MCP")
            
    except Exception as e:
        print(f"❌ Error during integration demo: {e}")
    
    print(f"\n✅ Integration demo completed")

if __name__ == "__main__":
    asyncio.run(main())
