"""
Tools for Incident Response Agent.
These tools provide functionality for repository analysis, log collection, and commit analysis.
"""

import os
import asyncio
import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RepositoryAnalysisTool:
    """Tool for analyzing repositories and discovering code paths."""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        self.github_api_url = "https://api.github.com"
    
    async def discover_repository_path(self, first_repo: str, error_description: str) -> Dict[str, Any]:
        """
        Discover the repository path from UI to GraphQL to Backend by analyzing code.
        
        Args:
            first_repo: The first repository to start analysis from
            error_description: Description of the error to understand the flow
            
        Returns:
            Dictionary containing the discovered repository path
        """
        print(f"🔍 Discovering repository path starting from: {first_repo}")
        
        # Simulate repository path discovery based on error description
        if "UI" in error_description or "Products page" in error_description:
            # UI error -> start with frontend, then follow to GraphQL, then backend
            repo_path = ["frontend-ui", "graphql-service", "backend-service"]
        elif "GraphQL" in error_description or "API" in error_description:
            # API error -> start with GraphQL, then backend
            repo_path = ["graphql-service", "backend-service"]
        else:
            # Default path
            repo_path = ["frontend-ui", "graphql-service", "backend-service"]
        
        all_repos = list(set(repo_path))  # Remove duplicates
        
        return {
            "repo_path": repo_path,
            "all_repos": all_repos,
            "path_reasoning": f"Based on error description '{error_description}', discovered path: {' -> '.join(repo_path)}",
            "confidence": 0.9
        }
    
    async def get_repository_commits(self, repo_name: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Get recent commits from a repository.
        
        Args:
            repo_name: Name of the repository
            hours_back: Number of hours to look back for commits
            
        Returns:
            List of commit information
        """
        print(f"📝 Getting commits for repository: {repo_name}")
        
        # Simulate getting commits from GitHub API
        since_date = datetime.now() - timedelta(hours=hours_back)
        
        # Simulated commit data
        commits = [
            {
                "sha": f"abc123_{repo_name}",
                "message": f"Update configuration in {repo_name}",
                "author": {
                    "name": "Developer",
                    "email": "developer@company.com"
                },
                "date": (datetime.now() - timedelta(hours=2)).isoformat(),
                "files": ["config.yaml", "deployment.yaml"],
                "repo": repo_name
            },
            {
                "sha": f"def456_{repo_name}",
                "message": f"Fix memory leak in {repo_name}",
                "author": {
                    "name": "Developer",
                    "email": "developer@company.com"
                },
                "date": (datetime.now() - timedelta(hours=4)).isoformat(),
                "files": ["service.py", "memory.py"],
                "repo": repo_name
            },
            {
                "sha": f"ghi789_{repo_name}",
                "message": f"Add new feature to {repo_name}",
                "author": {
                    "name": "Developer",
                    "email": "developer@company.com"
                },
                "date": (datetime.now() - timedelta(hours=6)).isoformat(),
                "files": ["feature.py", "test_feature.py"],
                "repo": repo_name
            }
        ]
        
        return commits
    
    async def analyze_code_dependencies(self, repo_name: str) -> Dict[str, Any]:
        """
        Analyze code dependencies to understand service relationships.
        
        Args:
            repo_name: Name of the repository to analyze
            
        Returns:
            Dictionary containing dependency analysis
        """
        print(f"🔗 Analyzing dependencies for repository: {repo_name}")
        
        # Simulate dependency analysis
        dependencies = {
            "frontend-ui": {
                "dependencies": ["graphql-service"],
                "api_endpoints": ["/api/graphql", "/api/products"],
                "service_type": "frontend"
            },
            "graphql-service": {
                "dependencies": ["backend-service"],
                "api_endpoints": ["/graphql"],
                "service_type": "api"
            },
            "backend-service": {
                "dependencies": ["database", "cache"],
                "api_endpoints": ["/api/v1/products"],
                "service_type": "backend"
            }
        }
        
        return dependencies.get(repo_name, {
            "dependencies": [],
            "api_endpoints": [],
            "service_type": "unknown"
        })


class LogCollectionTool:
    """Tool for collecting and analyzing logs from services."""
    
    def __init__(self):
        self.log_api_url = os.getenv("LOG_API_URL", "https://logs.company.com/api")
    
    async def get_service_logs(self, service_name: str, hours_back: int = 2) -> List[Dict[str, Any]]:
        """
        Get logs for a specific service.
        
        Args:
            service_name: Name of the service
            hours_back: Number of hours to look back for logs
            
        Returns:
            List of log entries
        """
        print(f"📊 Getting logs for service: {service_name}")
        
        # Simulate log collection
        logs = [
            {
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "level": "ERROR",
                "message": f"Memory usage at 95% in {service_name}",
                "service": service_name,
                "pod": f"{service_name}-pod-123",
                "namespace": "production"
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "level": "ERROR",
                "message": f"Out of memory error in {service_name}",
                "service": service_name,
                "pod": f"{service_name}-pod-123",
                "namespace": "production"
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
                "level": "WARN",
                "message": f"High memory usage detected in {service_name}",
                "service": service_name,
                "pod": f"{service_name}-pod-123",
                "namespace": "production"
            }
        ]
        
        return logs
    
    async def get_error_logs(self, service_name: str, hours_back: int = 2) -> List[Dict[str, Any]]:
        """
        Get error logs for a specific service.
        
        Args:
            service_name: Name of the service
            hours_back: Number of hours to look back for logs
            
        Returns:
            List of error log entries
        """
        print(f"🚨 Getting error logs for service: {service_name}")
        
        # Simulate error log collection
        error_logs = [
            {
                "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat(),
                "level": "ERROR",
                "message": f"Connection timeout to GraphQL service from {service_name}",
                "service": service_name,
                "error_code": "TIMEOUT",
                "stack_trace": "ConnectionError: timeout after 30s"
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "level": "ERROR",
                "message": f"Out of memory error in {service_name}",
                "service": service_name,
                "error_code": "OOM",
                "stack_trace": "MemoryError: Java heap space"
            }
        ]
        
        return error_logs


class CommitAnalysisTool:
    """Tool for analyzing commits and identifying potential issues."""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    async def analyze_commits_for_issues(self, commits: List[Dict[str, Any]], incident_description: str) -> Dict[str, Any]:
        """
        Analyze commits to identify potential issues related to the incident.
        
        Args:
            commits: List of commit information
            incident_description: Description of the incident
            
        Returns:
            Dictionary containing commit analysis results
        """
        print(f"🔍 Analyzing {len(commits)} commits for potential issues")
        
        suspicious_commits = []
        commit_based_actions = []
        
        # Analyze each commit
        for commit in commits:
            message = commit.get('message', '').lower()
            files = commit.get('files', [])
            
            # Check for configuration changes
            if any('config' in file.lower() for file in files):
                suspicious_commits.append({
                    "repo": commit.get('repo', 'unknown'),
                    "sha": commit.get('sha', 'unknown'),
                    "message": commit.get('message', ''),
                    "potential_issue": "Configuration change",
                    "confidence": 0.8,
                    "files": files
                })
                
                commit_based_actions.append({
                    "action": f"Review configuration changes in {commit.get('repo', 'unknown')}",
                    "priority": "high",
                    "reasoning": f"Configuration change detected in commit {commit.get('sha', 'unknown')}"
                })
            
            # Check for memory-related changes
            if 'memory' in message or 'oom' in message:
                suspicious_commits.append({
                    "repo": commit.get('repo', 'unknown'),
                    "sha": commit.get('sha', 'unknown'),
                    "message": commit.get('message', ''),
                    "potential_issue": "Memory-related change",
                    "confidence": 0.9,
                    "files": files
                })
                
                commit_based_actions.append({
                    "action": f"Investigate memory changes in {commit.get('repo', 'unknown')}",
                    "priority": "high",
                    "reasoning": f"Memory-related change detected in commit {commit.get('sha', 'unknown')}"
                })
            
            # Check for deployment changes
            if any('deploy' in file.lower() for file in files):
                suspicious_commits.append({
                    "repo": commit.get('repo', 'unknown'),
                    "sha": commit.get('sha', 'unknown'),
                    "message": commit.get('message', ''),
                    "potential_issue": "Deployment change",
                    "confidence": 0.7,
                    "files": files
                })
        
        return {
            "suspicious_commits": suspicious_commits,
            "commit_based_actions": commit_based_actions,
            "total_commits_analyzed": len(commits),
            "suspicious_commits_count": len(suspicious_commits)
        }


class LogAnalysisTool:
    """Tool for analyzing logs and identifying patterns."""
    
    def __init__(self):
        pass
    
    async def analyze_log_patterns(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze logs to identify patterns and errors.
        
        Args:
            logs: List of log entries
            
        Returns:
            Dictionary containing log analysis results
        """
        print(f"📊 Analyzing {len(logs)} log entries for patterns")
        
        error_logs = [log for log in logs if log.get('level') == 'ERROR']
        warning_logs = [log for log in logs if log.get('level') == 'WARN']
        
        # Identify patterns
        patterns = []
        if len(error_logs) > 0:
            patterns.append("High error rate detected")
        
        memory_errors = [log for log in error_logs if 'memory' in log.get('message', '').lower()]
        if len(memory_errors) > 0:
            patterns.append("Memory-related errors detected")
        
        timeout_errors = [log for log in error_logs if 'timeout' in log.get('message', '').lower()]
        if len(timeout_errors) > 0:
            patterns.append("Connection timeout errors detected")
        
        # Generate action items based on patterns
        log_based_actions = []
        
        if memory_errors:
            log_based_actions.append({
                "action": "Investigate memory usage and potential leaks",
                "priority": "high",
                "reasoning": f"Found {len(memory_errors)} memory-related errors"
            })
        
        if timeout_errors:
            log_based_actions.append({
                "action": "Check service connectivity and network issues",
                "priority": "medium",
                "reasoning": f"Found {len(timeout_errors)} timeout errors"
            })
        
        if len(error_logs) > 5:
            log_based_actions.append({
                "action": "Review recent deployments and configuration changes",
                "priority": "high",
                "reasoning": f"High error rate detected: {len(error_logs)} errors"
            })
        
        return {
            "log_patterns": patterns,
            "error_summary": f"Found {len(error_logs)} errors and {len(warning_logs)} warnings",
            "log_based_actions": log_based_actions,
            "total_logs": len(logs),
            "error_count": len(error_logs),
            "warning_count": len(warning_logs)
        }


class ParallelAnalysisTool:
    """Tool for performing parallel analysis of multiple repositories."""
    
    def __init__(self):
        self.repo_tool = RepositoryAnalysisTool()
        self.log_tool = LogCollectionTool()
        self.commit_tool = CommitAnalysisTool()
        self.log_analysis_tool = LogAnalysisTool()
    
    async def analyze_repositories_parallel(self, repos: List[str]) -> Dict[str, Any]:
        """
        Perform parallel analysis of multiple repositories.
        
        Args:
            repos: List of repository names to analyze
            
        Returns:
            Dictionary containing analysis results for all repositories
        """
        print(f"⚡ Starting parallel analysis of {len(repos)} repositories")
        
        # Create tasks for parallel execution
        tasks = []
        for repo in repos:
            tasks.append(self._analyze_single_repo(repo))
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        repo_commits = {}
        repo_logs = {}
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Error analyzing {repos[i]}: {result}")
                continue
            
            repo_name = repos[i]
            repo_commits[repo_name] = result.get('commits', [])
            repo_logs[repo_name] = result.get('logs', [])
        
        return {
            "repo_commits": repo_commits,
            "repo_logs": repo_logs,
            "repos_analyzed": len(repos),
            "successful_analyses": len([r for r in results if not isinstance(r, Exception)])
        }
    
    async def _analyze_single_repo(self, repo_name: str) -> Dict[str, Any]:
        """
        Analyze a single repository.
        
        Args:
            repo_name: Name of the repository to analyze
            
        Returns:
            Dictionary containing analysis results for the repository
        """
        try:
            # Get commits
            commits = await self.repo_tool.get_repository_commits(repo_name)
            
            # Get logs
            logs = await self.log_tool.get_service_logs(repo_name)
            
            return {
                "repo": repo_name,
                "commits": commits,
                "logs": logs
            }
        except Exception as e:
            print(f"❌ Error analyzing repository {repo_name}: {e}")
            return {
                "repo": repo_name,
                "commits": [],
                "logs": []
            }


# Export tools for use in the incident response agent
__all__ = [
    'RepositoryAnalysisTool',
    'LogCollectionTool', 
    'CommitAnalysisTool',
    'LogAnalysisTool',
    'ParallelAnalysisTool'
]
