"""
LangChain MCP Client for external server connections.
Uses langchain-mcp-adapters for seamless external MCP server integration.
"""

import asyncio
import os
import requests
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from ..types.state import GitCommit, InvestigationFinding, Recommendation


class LangChainMCPClient:
    """LangChain MCP Client for external server connections."""
    
    def __init__(self):
        self.client: Optional[MultiServerMCPClient] = None
        self.tools: Dict[str, Any] = {}
        self.github_tools: List[Any] = []
        self.jira_tools: List[Any] = []
        self.initialized = False
        
        # Direct Jira API client
        self.jira_url: Optional[str] = None
        self.jira_token: Optional[str] = None
        self.jira_email: Optional[str] = None
        self.jira_headers: Optional[Dict[str, str]] = None
    
    async def initialize(self, config: Dict[str, Any]):
        """Initialize LangChain MCP client with external servers."""
        try:
            print("🔗 Initializing LangChain MCP client with external servers...")
            
            # Build server configuration
            servers_config = {}
            
            # GitHub MCP Server
            github_mcp_url = os.getenv("MCP_GITHUB_SERVER_URL")
            github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
            
            if github_mcp_url and github_token:
                # For GitHub Enterprise (like Cisco's internal GitHub)
                github_host = os.getenv("GITHUB_HOST", "https://wwwin-github.cisco.com")
                
                servers_config["github"] = {
                    "transport": "streamable_http",
                    "url": github_mcp_url,
                    "headers": {
                        "Authorization": f"Bearer {github_token}",
                        "Accept": "application/vnd.github.v3+json",
                        "Content-Type": "application/json",
                        "User-Agent": "LangGraph-Incident-Response/1.0"
                    }
                }
                print(f"✅ GitHub Enterprise MCP server configured: {github_mcp_url}")
                print(f"   GitHub Host: {github_host}")
            
            # Jira MCP Server (try MCP first, fallback to direct API)
            jira_mcp_url = os.getenv("MCP_JIRA_SERVER_URL")
            jira_token = os.getenv("JIRA_TOKEN")
            jira_email = os.getenv("JIRA_EMAIL")
            
            # Store Jira credentials for direct API fallback
            self.jira_url = os.getenv("JIRA_URL")
            self.jira_token = jira_token
            self.jira_email = jira_email
            
            if jira_mcp_url and jira_token:
                try:
                    servers_config["jira"] = {
                        "transport": "streamable_http",
                        "url": jira_mcp_url,
                        "headers": {
                            "Authorization": f"Bearer {jira_token}",
                            "Content-Type": "application/json"
                        }
                    }
                    print(f"✅ Jira MCP server configured: {jira_mcp_url}")
                except Exception as e:
                    print(f"⚠️  Jira MCP server failed, will use direct API: {e}")
            else:
                print(f"⚠️  Jira MCP not configured, will use direct API")
            
            if not servers_config:
                print("⚠️  No external MCP servers configured")
                print("   Set MCP_GITHUB_SERVER_URL and/or MCP_JIRA_SERVER_URL in your .env file")
                return False
            
            # Initialize MultiServerMCPClient
            self.client = MultiServerMCPClient(servers_config)
            
            # Load tools from all servers
            tools_list = await self.client.get_tools()
            
            # Handle tools list format
            if isinstance(tools_list, list):
                self.tools = {tool.name: tool for tool in tools_list if hasattr(tool, 'name')}
            else:
                self.tools = tools_list
            
            # Separate tools by server
            for tool_name, tool in self.tools.items():
                if "github" in tool_name.lower() or "repo" in tool_name.lower() or "commit" in tool_name.lower():
                    self.github_tools.append(tool)
                elif "jira" in tool_name.lower() or "issue" in tool_name.lower() or "ticket" in tool_name.lower():
                    self.jira_tools.append(tool)
            
            print(f"✅ Loaded {len(self.tools)} tools from external MCP servers")
            print(f"   GitHub tools: {len(self.github_tools)}")
            print(f"   Jira tools: {len(self.jira_tools)}")
            
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize LangChain MCP client: {e}")
            return False
    
    async def get_github_commits(self, since_date: str, until_date: str, repo_owner: str = None, repo_name: str = None) -> List[GitCommit]:
        """Get GitHub commits using external MCP server."""
        if not self.initialized or not self.github_tools:
            print("❌ GitHub MCP tools not available")
            return []
        
        try:
            # Find the appropriate tool for getting commits
            commits_tool = None
            for tool in self.github_tools:
                if "commit" in tool.name.lower() or "repo" in tool.name.lower():
                    commits_tool = tool
                    break
            
            if not commits_tool:
                print("❌ No commit retrieval tool found in GitHub MCP server")
                return []
            
            # Call the tool
            result = await commits_tool.ainvoke({
                "since": since_date,
                "until": until_date,
                "owner": repo_owner,
                "repo": repo_name,
                "per_page": 50
            })
            
            # Parse results
            commits = []
            if result:
                # Handle different response formats
                if isinstance(result, str):
                    commit_data = json.loads(result)
                elif isinstance(result, dict):
                    commit_data = result.get("data", result)
                else:
                    commit_data = result
                
                if isinstance(commit_data, list):
                    for commit in commit_data:
                        commits.append(GitCommit(
                            sha=commit.get("sha", ""),
                            author=commit.get("commit", {}).get("author", {}).get("name", ""),
                            date=datetime.fromisoformat(commit.get("commit", {}).get("author", {}).get("date", "")),
                            message=commit.get("commit", {}).get("message", ""),
                            files=commit.get("files", []),
                            repository=f"{repo_owner}/{repo_name}"
                        ))
            
            print(f"✅ Retrieved {len(commits)} commits from external GitHub MCP server")
            return commits
            
        except Exception as e:
            print(f"❌ Error getting GitHub commits from external server: {e}")
            return []
    
    async def get_github_commits_multi_repo(self, since_date: str, until_date: str, repositories: List[Dict[str, str]]) -> List[GitCommit]:
        """Get GitHub commits from multiple repositories using external MCP server."""
        all_commits = []
        
        for repo in repositories:
            repo_owner = repo.get("owner")
            repo_name = repo.get("name")
            if repo_owner and repo_name:
                commits = await self.get_github_commits(since_date, until_date, repo_owner, repo_name)
                all_commits.extend(commits)
                print(f"📊 Found {len(commits)} commits in {repo_owner}/{repo_name}")
        
        return all_commits
    
    async def get_github_file_changes(self, commit_sha: str, repo_owner: str = None, repo_name: str = None) -> List[Dict[str, Any]]:
        """Get file changes for a specific commit using external MCP server."""
        if not self.initialized or not self.github_tools:
            return []
        
        try:
            # Find the appropriate tool for getting commit details
            commit_tool = None
            for tool in self.github_tools:
                if "commit" in tool.name.lower() and "detail" in tool.name.lower():
                    commit_tool = tool
                    break
            
            if not commit_tool:
                print("❌ No commit detail tool found in GitHub MCP server")
                return []
            
            # Call the tool
            result = await commit_tool.ainvoke({
                "sha": commit_sha,
                "owner": repo_owner,
                "repo": repo_name
            })
            
            # Parse results
            changes = []
            if result:
                if isinstance(result, str):
                    commit_data = json.loads(result)
                elif isinstance(result, dict):
                    commit_data = result.get("data", result)
                else:
                    commit_data = result
                
                files = commit_data.get("files", [])
                for file in files:
                    changes.append({
                        "filename": file.get("filename", ""),
                        "status": file.get("status", ""),
                        "additions": file.get("additions", 0),
                        "deletions": file.get("deletions", 0),
                        "patch": file.get("patch", "")
                    })
            
            return changes
            
        except Exception as e:
            print(f"❌ Error getting file changes from external server: {e}")
            return []
    
    async def create_jira_issue(self, summary: str, description: str, issue_type: str = "Incident", project_key: str = None) -> Optional[str]:
        """Create Jira issue using external MCP server or direct API."""
        # Try MCP first
        if self.initialized and self.jira_tools:
            try:
                # Find the appropriate tool for creating issues
                create_issue_tool = None
                for tool in self.jira_tools:
                    if "create" in tool.name.lower() and "issue" in tool.name.lower():
                        create_issue_tool = tool
                        break
                
                if create_issue_tool:
                    # Call the tool
                    result = await create_issue_tool.ainvoke({
                        "summary": summary,
                        "description": description,
                        "issuetype": {"name": issue_type}
                    })
                    
                    # Parse result
                    if result:
                        if isinstance(result, str):
                            issue_data = json.loads(result)
                        elif isinstance(result, dict):
                            issue_data = result.get("data", result)
                        else:
                            issue_data = result
                        
                        issue_key = issue_data.get("key")
                        if issue_key:
                            print(f"✅ Created Jira issue via MCP: {issue_key}")
                            return issue_key
            except Exception as e:
                print(f"⚠️  MCP issue creation failed, trying direct API: {e}")
        
        # Fallback to direct API
        return await self._create_jira_issue_direct(summary, description, issue_type, project_key)
    
    async def _create_jira_issue_direct(self, summary: str, description: str, issue_type: str = "Incident", project_key: str = None) -> Optional[str]:
        """Create Jira issue using direct API."""
        if not self.jira_url or not self.jira_token:
            print("❌ Jira credentials not configured for direct API")
            return None
        
        # Get project key if not provided
        if not project_key:
            project_key = await self._get_default_project_key()
            if not project_key:
                print("❌ No project key available for issue creation")
                return None
        
        try:
            # Try different authentication methods
            auth_methods = [
                {"Authorization": f"Bearer {self.jira_token}"},
                {"Authorization": f"Basic {base64.b64encode(f'{self.jira_email}:{self.jira_token}'.encode()).decode()}"} if self.jira_email else None,
                {"Authorization": f"token {self.jira_token}"},
            ]
            
            headers_base = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            for auth_header in auth_methods:
                if auth_header is None:
                    continue
                    
                try:
                    headers = {**headers_base, **auth_header}
                    url = f"{self.jira_url}/rest/api/3/issue"
                    data = {
                        "fields": {
                            "project": {"key": project_key},
                            "summary": summary,
                            "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]},
                            "issuetype": {"name": issue_type}
                        }
                    }
                    
                    response = requests.post(url, headers=headers, json=data, timeout=10)
                    
                    if response.status_code == 201:
                        issue_data = response.json()
                        issue_key = issue_data.get("key")
                        if issue_key:
                            print(f"✅ Created Jira issue via direct API: {issue_key}")
                            return issue_key
                    else:
                        print(f"⚠️  Direct API issue creation failed with {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️  Direct API method failed: {e}")
                    continue
            
            print("❌ All direct API authentication methods failed")
            return None
            
        except Exception as e:
            print(f"❌ Error in direct Jira API issue creation: {e}")
            return None
    
    async def _get_default_project_key(self) -> Optional[str]:
        """Get the first available project key."""
        if not self.jira_url or not self.jira_token:
            return None
        
        try:
            # Try different authentication methods
            auth_methods = [
                {"Authorization": f"Bearer {self.jira_token}"},
                {"Authorization": f"Basic {base64.b64encode(f'{self.jira_email}:{self.jira_token}'.encode()).decode()}"} if self.jira_email else None,
                {"Authorization": f"token {self.jira_token}"},
            ]
            
            headers_base = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            for auth_header in auth_methods:
                if auth_header is None:
                    continue
                    
                try:
                    headers = {**headers_base, **auth_header}
                    url = f"{self.jira_url}/rest/api/3/project"
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        projects = response.json()
                        if projects and len(projects) > 0:
                            return projects[0].get("key")
                    else:
                        print(f"⚠️  Direct API project fetch failed with {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️  Direct API method failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting default project key: {e}")
            return None
    
    async def update_jira_issue(self, issue_key: str, fields: Dict[str, Any]) -> bool:
        """Update Jira issue using external MCP server."""
        if not self.initialized or not self.jira_tools:
            return False
        
        try:
            # Find the appropriate tool for updating issues
            update_issue_tool = None
            for tool in self.jira_tools:
                if "update" in tool.name.lower() and "issue" in tool.name.lower():
                    update_issue_tool = tool
                    break
            
            if not update_issue_tool:
                print("❌ No issue update tool found in Jira MCP server")
                return False
            
            # Call the tool
            result = await update_issue_tool.ainvoke({
                "issueKey": issue_key,
                "fields": fields
            })
            
            if result:
                print(f"✅ Updated Jira issue: {issue_key}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error updating Jira issue via external server: {e}")
            return False
    
    async def add_jira_comment(self, issue_key: str, comment: str) -> bool:
        """Add comment to Jira issue using external MCP server."""
        if not self.initialized or not self.jira_tools:
            return False
        
        try:
            # Find the appropriate tool for adding comments
            comment_tool = None
            for tool in self.jira_tools:
                if "comment" in tool.name.lower():
                    comment_tool = tool
                    break
            
            if not comment_tool:
                print("❌ No comment tool found in Jira MCP server")
                return False
            
            # Call the tool
            result = await comment_tool.ainvoke({
                "issueKey": issue_key,
                "body": comment
            })
            
            if result:
                print(f"✅ Added comment to Jira issue: {issue_key}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error adding Jira comment via external server: {e}")
            return False
    
    async def search_jira_issues(self, jql: str) -> List[Dict[str, Any]]:
        """Search Jira issues using external MCP server or direct API."""
        # Try MCP first
        if self.initialized and self.jira_tools:
            try:
                # Find the appropriate tool for searching issues
                search_tool = None
                for tool in self.jira_tools:
                    if "search" in tool.name.lower() and "issue" in tool.name.lower():
                        search_tool = tool
                        break
                
                if search_tool:
                    # Call the tool
                    result = await search_tool.ainvoke({
                        "jql": jql,
                        "maxResults": 50
                    })
                    
                    # Parse results
                    issues = []
                    if result:
                        if isinstance(result, str):
                            search_data = json.loads(result)
                        elif isinstance(result, dict):
                            search_data = result.get("data", result)
                        else:
                            search_data = result
                        
                        issues = search_data.get("issues", [])
                    
                    return issues
            except Exception as e:
                print(f"⚠️  MCP search failed, trying direct API: {e}")
        
        # Fallback to direct API
        return await self._search_jira_issues_direct(jql)
    
    async def _search_jira_issues_direct(self, jql: str) -> List[Dict[str, Any]]:
        """Search Jira issues using direct API."""
        if not self.jira_url or not self.jira_token:
            print("❌ Jira credentials not configured for direct API")
            return []
        
        try:
            # Try different authentication methods
            auth_methods = [
                {"Authorization": f"Bearer {self.jira_token}"},
                {"Authorization": f"Basic {base64.b64encode(f'{self.jira_email}:{self.jira_token}'.encode()).decode()}"} if self.jira_email else None,
                {"Authorization": f"token {self.jira_token}"},
            ]
            
            headers_base = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            for auth_header in auth_methods:
                if auth_header is None:
                    continue
                    
                try:
                    headers = {**headers_base, **auth_header}
                    url = f"{self.jira_url}/rest/api/3/search"
                    data = {
                        "jql": jql,
                        "maxResults": 50,
                        "fields": ["summary", "status", "created", "project"]
                    }
                    
                    response = requests.post(url, headers=headers, json=data, timeout=10)
                    
                    if response.status_code == 200:
                        search_data = response.json()
                        issues = search_data.get("issues", [])
                        print(f"✅ Direct Jira API search successful: {len(issues)} issues found")
                        return issues
                    else:
                        print(f"⚠️  Direct API search failed with {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️  Direct API method failed: {e}")
                    continue
            
            print("❌ All direct API authentication methods failed")
            return []
            
        except Exception as e:
            print(f"❌ Error in direct Jira API search: {e}")
            return []
    
    async def close(self):
        """Close LangChain MCP client connections."""
        if self.client:
            try:
                await self.client.aclose()
                print("✅ LangChain MCP client connections closed")
            except Exception as e:
                print(f"⚠️  Error closing LangChain MCP client: {e}")


# Global instance
langchain_mcp_client = LangChainMCPClient()
