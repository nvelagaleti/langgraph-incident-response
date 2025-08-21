#!/usr/bin/env python3
"""
Get Jira Projects
Connect to Jira and retrieve all available projects using token management
"""

import os
import asyncio
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from token_manager import TokenManager
from mcp_client_with_token_manager import MCPClientWithTokenManager

class JiraProjectManager:
    """Manages Jira project operations with automatic token management."""
    
    def __init__(self):
        load_dotenv()
        self.token_manager = TokenManager()
        self.mcp_client = None
        self.jira_url = os.getenv("JIRA_URL")
        
    async def initialize(self):
        """Initialize the MCP client with token management."""
        print("🚀 Initializing Jira Project Manager")
        print("=" * 50)
        
        # Ensure we have a valid token
        token = await self.token_manager.ensure_valid_token()
        if not token:
            print("❌ Failed to obtain valid token")
            return False
        
        print(f"✅ Token validated successfully")
        print(f"🌐 Jira URL: {self.jira_url or 'Using default Atlassian API'}")
        
        # Initialize MCP client
        self.mcp_client = MCPClientWithTokenManager()
        success = await self.mcp_client.initialize()
        
        if success:
            print("✅ MCP client initialized successfully")
            return True
        else:
            print("❌ Failed to initialize MCP client")
            return False
    
    async def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all available Jira projects."""
        print("\n🔍 Retrieving All Jira Projects")
        print("-" * 40)
        
        if not self.mcp_client:
            print("❌ MCP client not initialized")
            return []
        
        try:
            # Get tools
            tools = await self.mcp_client.get_tools()
            
            # Find the get_projects tool
            get_projects_tool = None
            for tool in tools:
                if hasattr(tool, 'name') and tool.name == 'get_projects':
                    get_projects_tool = tool
                    break
            
            if not get_projects_tool:
                print("❌ get_projects tool not found")
                print("📋 Available tools:")
                for tool in tools:
                    if hasattr(tool, 'name'):
                        print(f"   - {tool.name}")
                return []
            
            print("✅ Found get_projects tool")
            
            # Invoke the tool to get projects
            print("🔄 Fetching projects...")
            result = await get_projects_tool.ainvoke({})
            
            # Parse the result
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
            
            print(f"✅ Retrieved {len(projects)} projects")
            return projects
            
        except Exception as e:
            print(f"❌ Error getting projects: {e}")
            return []
    
    def display_projects(self, projects: List[Dict[str, Any]]):
        """Display projects in a formatted way."""
        print(f"\n📋 Jira Projects ({len(projects)} total)")
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
            print(f"   🎨 Avatar: {project.get('avatarUrls', {}).get('48x48', 'N/A')}")
            
            # Additional details if available
            if 'lead' in project:
                print(f"   👤 Lead: {project['lead'].get('displayName', 'N/A')}")
            
            if 'projectCategory' in project:
                print(f"   📂 Category: {project['projectCategory'].get('name', 'N/A')}")
            
            if 'simplified' in project:
                print(f"   ⚡ Simplified: {project['simplified']}")
    
    def save_projects_to_file(self, projects: List[Dict[str, Any]], filename: str = "jira_projects.json"):
        """Save projects to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(projects, f, indent=2)
            print(f"\n💾 Projects saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving projects to file: {e}")
    
    async def get_project_details(self, project_key: str) -> Dict[str, Any]:
        """Get detailed information for a specific project."""
        print(f"\n🔍 Getting Details for Project: {project_key}")
        print("-" * 40)
        
        if not self.mcp_client:
            print("❌ MCP client not initialized")
            return {}
        
        try:
            tools = await self.mcp_client.get_tools()
            
            # Find the get_project tool
            get_project_tool = None
            for tool in tools:
                if hasattr(tool, 'name') and tool.name == 'get_project':
                    get_project_tool = tool
                    break
            
            if not get_project_tool:
                print("❌ get_project tool not found")
                return {}
            
            # Get project details
            result = await get_project_tool.ainvoke({
                "project_key": project_key
            })
            
            if isinstance(result, str):
                try:
                    project_data = json.loads(result)
                except json.JSONDecodeError:
                    print("❌ Failed to parse project data")
                    return {}
            else:
                project_data = result
            
            print(f"✅ Retrieved details for project {project_key}")
            return project_data
            
        except Exception as e:
            print(f"❌ Error getting project details: {e}")
            return {}
    
    async def close(self):
        """Close the MCP client."""
        if self.mcp_client:
            await self.mcp_client.close()

async def main():
    """Main function to get Jira projects."""
    print("🚀 Jira Projects Retrieval")
    print("=" * 60)
    
    # Initialize project manager
    project_manager = JiraProjectManager()
    
    # Initialize connection
    success = await project_manager.initialize()
    if not success:
        print("❌ Failed to initialize project manager")
        return
    
    try:
        # Get all projects
        projects = await project_manager.get_all_projects()
        
        if projects:
            # Display projects
            project_manager.display_projects(projects)
            
            # Save to file
            project_manager.save_projects_to_file(projects)
            
            # Get details for first project (if available)
            if projects:
                first_project = projects[0]
                project_key = first_project.get('key')
                if project_key:
                    print(f"\n🔍 Getting detailed info for first project: {project_key}")
                    details = await project_manager.get_project_details(project_key)
                    if details:
                        print(f"📄 Project details: {json.dumps(details, indent=2)[:500]}...")
            
            print(f"\n🎉 Successfully retrieved {len(projects)} Jira projects!")
            
        else:
            print("❌ No projects found or failed to retrieve projects")
            
    except Exception as e:
        print(f"❌ Error during project retrieval: {e}")
    
    finally:
        # Clean up
        await project_manager.close()
        print("\n✅ Project manager closed")

if __name__ == "__main__":
    asyncio.run(main())
