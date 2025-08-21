"""
Direct Jira API Client
Direct API integration for Jira operations without MCP complexity
"""

import os
import requests
import base64
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

class DirectJiraClient:
    """Direct Jira API client for incident response operations."""
    
    def __init__(self):
        load_dotenv()
        self.jira_url = os.getenv("JIRA_URL")
        self.jira_token = os.getenv("JIRA_TOKEN")
        self.jira_email = os.getenv("JIRA_EMAIL")
        self.headers = None
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate with Jira using different methods."""
        if not self.jira_url or not self.jira_token:
            print("❌ Jira configuration missing")
            return False
        
        # Try different authentication methods
        auth_methods = [
            ("Basic Auth", {"Authorization": f"Basic {base64.b64encode(f'{self.jira_email}:{self.jira_token}'.encode()).decode()}"} if self.jira_email else None),
            ("Bearer Token", {"Authorization": f"Bearer {self.jira_token}"}),
            ("Token Only", {"Authorization": f"token {self.jira_token}"}),
        ]
        
        headers_base = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        for method_name, auth_header in auth_methods:
            if auth_header is None:
                continue
                
            try:
                headers = {**headers_base, **auth_header}
                user_url = f"{self.jira_url}/rest/api/3/myself"
                response = requests.get(user_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    self.headers = headers
                    self.authenticated = True
                    print(f"✅ Authenticated with {method_name}")
                    print(f"📄 User: {user_data.get('displayName', 'Unknown')}")
                    return True
                else:
                    print(f"❌ {method_name} failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {method_name} error: {e}")
                continue
        
        print("❌ All authentication methods failed")
        return False
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all accessible projects."""
        if not self.authenticated:
            print("❌ Not authenticated")
            return []
        
        try:
            url = f"{self.jira_url}/rest/api/3/project"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                projects = response.json()
                print(f"✅ Retrieved {len(projects)} projects")
                return projects
            else:
                print(f"❌ Failed to get projects: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting projects: {e}")
            return []
    
    def get_project(self, project_key: str) -> Optional[Dict[str, Any]]:
        """Get specific project details."""
        if not self.authenticated:
            print("❌ Not authenticated")
            return None
        
        try:
            url = f"{self.jira_url}/rest/api/3/project/{project_key}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                project = response.json()
                print(f"✅ Retrieved project {project_key}")
                return project
            else:
                print(f"❌ Failed to get project {project_key}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting project {project_key}: {e}")
            return None
    
    def search_issues(self, jql: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Search issues using JQL."""
        if not self.authenticated:
            print("❌ Not authenticated")
            return []
        
        try:
            url = f"{self.jira_url}/rest/api/3/search"
            data = {
                "jql": jql,
                "maxResults": max_results,
                "fields": ["summary", "status", "created", "project", "issuetype"]
            }
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 200:
                search_data = response.json()
                issues = search_data.get("issues", [])
                print(f"✅ Found {len(issues)} issues")
                return issues
            else:
                print(f"❌ Failed to search issues: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error searching issues: {e}")
            return []
    
    def create_issue(self, project_key: str, summary: str, description: str, issue_type: str = "Incident") -> Optional[str]:
        """Create a new issue."""
        if not self.authenticated:
            print("❌ Not authenticated")
            return None
        
        try:
            url = f"{self.jira_url}/rest/api/3/issue"
            data = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": description}]
                            }
                        ]
                    },
                    "issuetype": {"name": issue_type}
                }
            }
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                issue_data = response.json()
                issue_key = issue_data.get("key")
                print(f"✅ Created issue: {issue_key}")
                return issue_key
            else:
                print(f"❌ Failed to create issue: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating issue: {e}")
            return None
    
    def add_comment(self, issue_key: str, comment: str) -> bool:
        """Add a comment to an issue."""
        if not self.authenticated:
            print("❌ Not authenticated")
            return False
        
        try:
            url = f"{self.jira_url}/rest/api/3/issue/{issue_key}/comment"
            data = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": comment}]
                        }
                    ]
                }
            }
            
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                print(f"✅ Added comment to {issue_key}")
                return True
            else:
                print(f"❌ Failed to add comment: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding comment: {e}")
            return False
    
    def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> bool:
        """Update issue fields."""
        if not self.authenticated:
            print("❌ Not authenticated")
            return False
        
        try:
            url = f"{self.jira_url}/rest/api/3/issue/{issue_key}"
            data = {"fields": fields}
            
            response = requests.put(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 204:
                print(f"✅ Updated issue {issue_key}")
                return True
            else:
                print(f"❌ Failed to update issue: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating issue: {e}")
            return False
    
    def get_issue_types(self, project_key: str) -> List[Dict[str, Any]]:
        """Get issue types for a project."""
        if not self.authenticated:
            print("❌ Not authenticated")
            return []
        
        try:
            url = f"{self.jira_url}/rest/api/3/project/{project_key}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                project_data = response.json()
                issue_types = project_data.get("issueTypes", [])
                print(f"✅ Retrieved {len(issue_types)} issue types for {project_key}")
                return issue_types
            else:
                print(f"❌ Failed to get issue types: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting issue types: {e}")
            return []

# Global instance
direct_jira_client = DirectJiraClient()
