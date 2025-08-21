"""
MCP Client Service for LangGraph Incident Response System.
Integrates with GitHub and Jira MCP servers for real data access.
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from modelcontextprotocol import ClientSession, StdioServerParameters
from modelcontextprotocol.client import Client
from modelcontextprotocol.models import (
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    Tool,
    ToolResult
)

from ..types.state import GitCommit, InvestigationFinding, Recommendation


class MCPClientService:
    """
    MCP Client Service for integrating with GitHub and Jira MCP servers.
    Provides real data access for incident response.
    """
    
    def __init__(self):
        self.github_client: Optional[Client] = None
        self.jira_client: Optional[Client] = None
        self.github_session: Optional[ClientSession] = None
        self.jira_session: Optional[ClientSession] = None
        # Multi-repo support
        self.github_sessions: Dict[str, ClientSession] = {}
        self.github_token: Optional[str] = None
    
    async def initialize_github_mcp(self, github_token: str = None, repo_owner: str = None, repo_name: str = None, external_server_url: str = None):
        """Initialize GitHub MCP client."""
        try:
            if external_server_url:
                # Use external MCP server (HTTP-based)
                print(f"🔗 Connecting to external GitHub MCP server: {external_server_url}")
                
                # For HTTP-based MCP servers, we need to use HTTP client
                # The GitHub MCP server exposes HTTP endpoints
                try:
                    import httpx
                    
                    # Test connection to external server
                    async with httpx.AsyncClient() as client:
                        response = await client.get(f"{external_server_url}/health")
                        if response.status_code == 200:
                            print(f"✅ External GitHub MCP server is healthy")
                            
                            # Store external server URL for HTTP-based calls
                            self.github_external_url = external_server_url
                            self.github_client = "external"  # Mark as external
                            
                        else:
                            print(f"❌ External server health check failed: {response.status_code}")
                            self.github_client = None
                            
                except Exception as e:
                    print(f"❌ Failed to connect to external GitHub MCP server: {e}")
                    self.github_client = None
                
            else:
                # Store token for multi-repo support
                self.github_token = github_token
                
                if repo_owner and repo_name:
                    # Initialize specific repository
                    await self._initialize_single_repo(repo_owner, repo_name)
                else:
                    # Initialize for multi-repo support (no specific repo)
                    print(f"✅ GitHub MCP client initialized for multi-repo support")
            
        except Exception as e:
            print(f"❌ Failed to initialize GitHub MCP client: {e}")
            self.github_client = None
    
    async def _initialize_single_repo(self, repo_owner: str, repo_name: str):
        """Initialize MCP session for a specific repository."""
        repo_key = f"{repo_owner}/{repo_name}"
        
        if repo_key in self.github_sessions:
            # Reuse existing session
            self.github_session = self.github_sessions[repo_key]
            self.github_client = self.github_session.client
            print(f"✅ Reusing existing GitHub MCP session for {repo_key}")
            return
        
        # Create new session for this repository
        github_params = StdioServerParameters(
            command="npx",
            args=[
                "@modelcontextprotocol/server-github",
                "--token", self.github_token,
                "--owner", repo_owner,
                "--repo", repo_name
            ]
        )
        
        # Create client session
        session = ClientSession(
            server=github_params,
            client=Client(
                name="langgraph-incident-response",
                version="1.0.0"
            )
        )
        
        # Initialize the session
        await session.initialize()
        
        # Store session for reuse
        self.github_sessions[repo_key] = session
        self.github_session = session
        self.github_client = session.client
        
        print(f"✅ GitHub MCP client initialized for {repo_key}")
    
    async def get_repo_session(self, repo_owner: str, repo_name: str) -> Optional[ClientSession]:
        """Get or create MCP session for a specific repository."""
        repo_key = f"{repo_owner}/{repo_name}"
        
        if repo_key not in self.github_sessions:
            if not self.github_token:
                print(f"❌ GitHub token not available for {repo_key}")
                return None
            
            await self._initialize_single_repo(repo_owner, repo_name)
        
        return self.github_sessions.get(repo_key)
    
    async def initialize_jira_mcp(self, jira_url: str = None, jira_token: str = None, project_key: str = None, external_server_url: str = None):
        """Initialize Jira MCP client."""
        try:
            if external_server_url:
                # Use external MCP server
                jira_params = StdioServerParameters(
                    command="curl",
                    args=["-s", external_server_url]
                )
                print(f"🔗 Connecting to external Jira MCP server: {external_server_url}")
            else:
                # Use local MCP server
                jira_params = StdioServerParameters(
                    command="npx",
                    args=[
                        "@modelcontextprotocol/server-jira",
                        "--url", jira_url,
                        "--token", jira_token,
                        "--project", project_key
                    ]
                )
                print(f"🔗 Connecting to local Jira MCP server for project {project_key}")
            
            # Create client session
            self.jira_session = ClientSession(
                server=jira_params,
                client=Client(
                    name="langgraph-incident-response",
                    version="1.0.0"
                )
            )
            
            # Initialize the session
            await self.jira_session.initialize()
            self.jira_client = self.jira_session.client
            
            if external_server_url:
                print(f"✅ Jira MCP client connected to external server")
            else:
                print(f"✅ Jira MCP client initialized for project {project_key}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Jira MCP client: {e}")
            self.jira_client = None
    
    async def get_github_commits(self, since_date: str, until_date: str, repo_owner: str = None, repo_name: str = None) -> List[GitCommit]:
        """Get GitHub commits using MCP for a specific repository."""
        if not self.github_token:
            return []
        
        try:
            # Check if using external server
            if self.github_client == "external":
                return await self._get_github_commits_external(since_date, until_date, repo_owner, repo_name)
            
            # Use local MCP server
            session = await self.get_repo_session(repo_owner, repo_name)
            if not session:
                print(f"❌ No session available for {repo_owner}/{repo_name}")
                return []
            
            # Get available tools
            tools = await session.list_tools()
            
            # Find the get_commits tool
            commits_tool = None
            for tool in tools.tools:
                if tool.name == "get_commits":
                    commits_tool = tool
                    break
            
            if not commits_tool:
                print("❌ get_commits tool not found in GitHub MCP server")
                return []
            
            # Call the tool
            result = await session.call_tool(
                name="get_commits",
                arguments={
                    "since": since_date,
                    "until": until_date,
                    "per_page": 50
                }
            )
            
            # Parse results
            commits = []
            if result.content:
                for content in result.content:
                    if isinstance(content, TextContent):
                        # Parse the JSON response
                        commit_data = json.loads(content.text)
                        for commit in commit_data:
                            commits.append(GitCommit(
                                sha=commit.get("sha", ""),
                                author=commit.get("commit", {}).get("author", {}).get("name", ""),
                                date=datetime.fromisoformat(commit.get("commit", {}).get("author", {}).get("date", "")),
                                message=commit.get("commit", {}).get("message", ""),
                                files=commit.get("files", []),
                                repository=f"{repo_owner}/{repo_name}"
                            ))
            
            return commits
            
        except Exception as e:
            print(f"❌ Error getting GitHub commits for {repo_owner}/{repo_name}: {e}")
            return []
    
    async def _get_github_commits_external(self, since_date: str, until_date: str, repo_owner: str = None, repo_name: str = None) -> List[GitCommit]:
        """Get GitHub commits using external HTTP-based MCP server."""
        try:
            import httpx
            
            # Call external GitHub MCP server
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.github_external_url}/tools/get_commits",
                    headers={
                        "Authorization": f"Bearer {self.github_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "owner": repo_owner,
                        "repo": repo_name,
                        "since": since_date,
                        "until": until_date,
                        "per_page": 50
                    }
                )
                
                if response.status_code == 200:
                    commit_data = response.json()
                    commits = []
                    
                    for commit in commit_data:
                        commits.append(GitCommit(
                            sha=commit.get("sha", ""),
                            author=commit.get("commit", {}).get("author", {}).get("name", ""),
                            date=datetime.fromisoformat(commit.get("commit", {}).get("author", {}).get("date", "")),
                            message=commit.get("commit", {}).get("message", ""),
                            files=commit.get("files", []),
                            repository=f"{repo_owner}/{repo_name}"
                        ))
                    
                    return commits
                else:
                    print(f"❌ External server error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            print(f"❌ Error calling external GitHub MCP server: {e}")
            return []
    
    async def get_github_commits_multi_repo(self, since_date: str, until_date: str, repositories: List[Dict[str, str]]) -> List[GitCommit]:
        """Get GitHub commits from multiple repositories."""
        all_commits = []
        
        for repo in repositories:
            repo_owner = repo.get("owner")
            repo_name = repo.get("name")
            
            if repo_owner and repo_name:
                commits = await self.get_github_commits(since_date, until_date, repo_owner, repo_name)
                all_commits.extend(commits)
                print(f"📊 Found {len(commits)} commits in {repo_owner}/{repo_name}")
        
        return all_commits
    
    async def get_github_file_changes(self, commit_sha: str) -> List[Dict[str, Any]]:
        """Get file changes for a specific commit."""
        if not self.github_client:
            return []
        
        try:
            result = await self.github_session.call_tool(
                name="get_commit",
                arguments={
                    "sha": commit_sha
                }
            )
            
            changes = []
            if result.content:
                for content in result.content:
                    if isinstance(content, TextContent):
                        commit_data = json.loads(content.text)
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
            print(f"❌ Error getting file changes: {e}")
            return []
    
    async def create_jira_issue(self, summary: str, description: str, issue_type: str = "Incident") -> Optional[str]:
        """Create a Jira issue using MCP."""
        if not self.jira_client:
            return None
        
        try:
            result = await self.jira_session.call_tool(
                name="create_issue",
                arguments={
                    "summary": summary,
                    "description": description,
                    "issuetype": issue_type,
                    "project": self.jira_session.server.args[3]
                }
            )
            
            if result.content:
                for content in result.content:
                    if isinstance(content, TextContent):
                        issue_data = json.loads(content.text)
                        return issue_data.get("key", None)
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating Jira issue: {e}")
            return None
    
    async def update_jira_issue(self, issue_key: str, fields: Dict[str, Any]) -> bool:
        """Update a Jira issue using MCP."""
        if not self.jira_client:
            return False
        
        try:
            result = await self.jira_session.call_tool(
                name="update_issue",
                arguments={
                    "issue_key": issue_key,
                    "fields": fields
                }
            )
            
            return result.content is not None
            
        except Exception as e:
            print(f"❌ Error updating Jira issue: {e}")
            return False
    
    async def add_jira_comment(self, issue_key: str, comment: str) -> bool:
        """Add a comment to a Jira issue using MCP."""
        if not self.jira_client:
            return False
        
        try:
            result = await self.jira_session.call_tool(
                name="add_comment",
                arguments={
                    "issue_key": issue_key,
                    "comment": comment
                }
            )
            
            return result.content is not None
            
        except Exception as e:
            print(f"❌ Error adding Jira comment: {e}")
            return False
    
    async def search_jira_issues(self, jql: str) -> List[Dict[str, Any]]:
        """Search Jira issues using MCP."""
        if not self.jira_client:
            return []
        
        try:
            result = await self.jira_session.call_tool(
                name="search_issues",
                arguments={
                    "jql": jql,
                    "max_results": 50
                }
            )
            
            issues = []
            if result.content:
                for content in result.content:
                    if isinstance(content, TextContent):
                        search_data = json.loads(content.text)
                        issues = search_data.get("issues", [])
            
            return issues
            
        except Exception as e:
            print(f"❌ Error searching Jira issues: {e}")
            return []
    
    async def close(self):
        """Close MCP sessions."""
        if self.github_session:
            await self.github_session.close()
        if self.jira_session:
            await self.jira_session.close()


# Global MCP client instance
mcp_client = MCPClientService()

