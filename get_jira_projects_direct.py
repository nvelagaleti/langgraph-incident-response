#!/usr/bin/env python3
"""
Get Jira Projects (Direct API)
Connect to Jira and retrieve all available projects using direct API calls
"""

import os
import asyncio
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
from token_manager import TokenManager

class JiraDirectProjectManager:
    """Manages Jira project operations using direct API calls."""
    
    def __init__(self):
        load_dotenv()
        self.token_manager = TokenManager()
        self.jira_url = os.getenv("JIRA_URL", "https://mailtosimha.atlassian.net")
        self.access_token = None
        
    async def initialize(self):
        """Initialize with valid token."""
        print("🚀 Initializing Jira Direct Project Manager")
        print("=" * 50)
        
        # Ensure we have a valid token
        self.access_token = await self.token_manager.ensure_valid_token()
        if not self.access_token:
            print("❌ Failed to obtain valid token")
            return False
        
        print(f"✅ Token validated successfully")
        print(f"🌐 Jira URL: {self.jira_url}")
        
        return True
    
    def get_headers(self):
        """Get headers for API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all available Jira projects using direct API."""
        print("\n🔍 Retrieving All Jira Projects")
        print("-" * 40)
        
        try:
            # First, get accessible resources to find the cloud ID
            print("🔄 Getting accessible resources...")
            resources_url = "https://api.atlassian.com/oauth/token/accessible-resources"
            response = requests.get(resources_url, headers=self.get_headers())
            
            if response.status_code != 200:
                print(f"❌ Failed to get accessible resources: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return []
            
            resources = response.json()
            print(f"✅ Found {len(resources)} accessible resources")
            
            all_projects = []
            
            for resource in resources:
                cloud_id = resource.get('id')
                name = resource.get('name', 'Unknown')
                print(f"\n🔍 Processing resource: {name} (ID: {cloud_id})")
                
                # Get projects for this cloud ID
                projects_url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/project"
                project_response = requests.get(projects_url, headers=self.get_headers())
                
                if project_response.status_code == 200:
                    projects = project_response.json()
                    print(f"✅ Found {len(projects)} projects in {name}")
                    
                    # Add cloud info to each project
                    for project in projects:
                        project['cloud_id'] = cloud_id
                        project['cloud_name'] = name
                    
                    all_projects.extend(projects)
                else:
                    print(f"❌ Failed to get projects for {name}: {project_response.status_code}")
                    print(f"📄 Response: {project_response.text}")
            
            print(f"\n✅ Total projects retrieved: {len(all_projects)}")
            return all_projects
            
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
        
        # Group projects by cloud
        clouds = {}
        for project in projects:
            cloud_name = project.get('cloud_name', 'Unknown')
            if cloud_name not in clouds:
                clouds[cloud_name] = []
            clouds[cloud_name].append(project)
        
        for cloud_name, cloud_projects in clouds.items():
            print(f"\n🌐 Cloud: {cloud_name} ({len(cloud_projects)} projects)")
            print("-" * 40)
            
            for i, project in enumerate(cloud_projects, 1):
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
    
    def save_projects_to_file(self, projects: List[Dict[str, Any]], filename: str = "jira_projects_direct.json"):
        """Save projects to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(projects, f, indent=2)
            print(f"\n💾 Projects saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving projects to file: {e}")
    
    async def get_project_details(self, project_key: str, cloud_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific project."""
        print(f"\n🔍 Getting Details for Project: {project_key}")
        print("-" * 40)
        
        try:
            project_url = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3/project/{project_key}"
            response = requests.get(project_url, headers=self.get_headers())
            
            if response.status_code == 200:
                project_data = response.json()
                print(f"✅ Retrieved details for project {project_key}")
                return project_data
            else:
                print(f"❌ Failed to get project details: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Error getting project details: {e}")
            return {}
    
    async def test_connection(self):
        """Test the connection to Jira."""
        print("\n🧪 Testing Jira Connection")
        print("-" * 30)
        
        try:
            # Test with accessible resources endpoint
            resources_url = "https://api.atlassian.com/oauth/token/accessible-resources"
            response = requests.get(resources_url, headers=self.get_headers())
            
            if response.status_code == 200:
                resources = response.json()
                print(f"✅ Connection successful!")
                print(f"📊 Accessible resources: {len(resources)}")
                
                for resource in resources:
                    print(f"   • {resource.get('name', 'Unknown')} (ID: {resource.get('id', 'N/A')})")
                
                return True
            else:
                print(f"❌ Connection failed: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

async def main():
    """Main function to get Jira projects."""
    print("🚀 Jira Projects Retrieval (Direct API)")
    print("=" * 60)
    
    # Initialize project manager
    project_manager = JiraDirectProjectManager()
    
    # Initialize connection
    success = await project_manager.initialize()
    if not success:
        print("❌ Failed to initialize project manager")
        return
    
    try:
        # Test connection first
        connection_ok = await project_manager.test_connection()
        if not connection_ok:
            print("❌ Connection test failed")
            return
        
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
                cloud_id = first_project.get('cloud_id')
                if project_key and cloud_id:
                    print(f"\n🔍 Getting detailed info for first project: {project_key}")
                    details = await project_manager.get_project_details(project_key, cloud_id)
                    if details:
                        print(f"📄 Project details: {json.dumps(details, indent=2)[:500]}...")
            
            print(f"\n🎉 Successfully retrieved {len(projects)} Jira projects!")
            
        else:
            print("❌ No projects found or failed to retrieve projects")
            
    except Exception as e:
        print(f"❌ Error during project retrieval: {e}")
    
    print("\n✅ Project manager completed")

if __name__ == "__main__":
    asyncio.run(main())
