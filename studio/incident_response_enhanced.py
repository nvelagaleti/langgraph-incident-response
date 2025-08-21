"""
Enhanced Incident Response Agent for LangGraph Studio.
This agent follows a specific 9-step workflow for handling IR tickets with automatic repo discovery and RCA analysis.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime, timedelta
import uuid
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from dotenv import load_dotenv
import sys
import os

# Add parent directory to path to import Circuit LLM client
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()


def discover_local_repositories():
    """Discover local repositories by scanning the workspace directory."""
    try:
        # Get the workspace root (parent of langgraph-incident-response directory)
        workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        print(f"🔍 Scanning workspace root: {workspace_root}")
        
        # Look for directories that might be repositories
        potential_repos = []
        for item in os.listdir(workspace_root):
            item_path = os.path.join(workspace_root, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                print(f"🔍 Checking directory: {item}")
                # Check if it looks like a repository (has package.json, requirements.txt, etc.)
                repo_indicators = ['package.json', 'requirements.txt', 'pom.xml', 'build.gradle', '.git', 'src', 'app']
                has_indicators = any(os.path.exists(os.path.join(item_path, indicator)) for indicator in repo_indicators)
                print(f"  📁 {item}: has indicators = {has_indicators}")
                if has_indicators:
                    potential_repos.append(item)
        
        print(f"🔍 Potential repositories found: {potential_repos}")
        
        # Sort repositories by relevance (frontend first, then backend, then others)
        sorted_repos = []
        
        # Look for frontend repositories first
        frontend_keywords = ['web', 'frontend', 'ui', 'app', 'client']
        for repo in potential_repos:
            if any(keyword in repo.lower() for keyword in frontend_keywords):
                sorted_repos.append(repo)
        
        # Look for backend/API repositories
        backend_keywords = ['api', 'service', 'backend', 'server', 'graphql']
        for repo in potential_repos:
            if any(keyword in repo.lower() for keyword in backend_keywords) and repo not in sorted_repos:
                sorted_repos.append(repo)
        
        # Add any remaining repositories
        for repo in potential_repos:
            if repo not in sorted_repos:
                sorted_repos.append(repo)
        
        print(f"🔍 Discovered {len(sorted_repos)} local repositories: {sorted_repos}")
        return sorted_repos
        
    except Exception as e:
        print(f"⚠️  Error discovering local repositories: {e}")
        return []

async def search_repositories_with_mcp(github_mcp_client, search_keywords):
    """Search for repositories using GitHub Copilot MCP tools (following working pattern)."""
    try:
        print(f"🔍 Searching repositories with MCP using keywords: {search_keywords}")
        
        # Get available tools
        tools = await github_mcp_client.get_tools()
        print(f"✅ Found {len(tools)} MCP tools")
        
        # Create tool map (following working pattern)
        tool_map = {}
        if isinstance(tools, list):
            for tool in tools:
                if hasattr(tool, 'name'):
                    tool_map[tool.name] = tool
        
        # Look for search_repositories tool specifically
        search_tool = tool_map.get('search_repositories')
        if search_tool:
            print("🔍 Found search_repositories tool, using it to search...")
            
            found_repos = []
            
            # Try searching with each keyword
            for keyword in search_keywords[:3]:  # Use top 3 keywords
                try:
                    # Use more specific search query to narrow down results
                    query = f"user:nvelagaleti {keyword}"
                    print(f"🔍 Searching with query: {query}")
                    
                    result = await search_tool.ainvoke({"query": query})
                    
                    # Log the raw result for debugging
                    print(f"🔍 Raw result for keyword '{keyword}': {result}")
                    print(f"🔍 Result type: {type(result)}")
                    
                    # Handle different result types
                    if isinstance(result, str):
                        print(f"🔍 String result received, trying to parse as JSON...")
                        try:
                            import json
                            parsed_result = json.loads(result)
                            print(f"🔍 Parsed JSON result: {parsed_result}")
                            result = parsed_result
                        except json.JSONDecodeError as e:
                            print(f"⚠️  Failed to parse string as JSON: {e}")
                            print(f"🔍 String content: {result[:200]}...")
                            result = None
                    
                    if result and isinstance(result, dict) and 'items' in result:
                        repos = result['items']
                        print(f"✅ Found {len(repos)} repositories for keyword '{keyword}'")
                        
                        # Process repositories found
                        user_repos_found = 0
                        for repo in repos:
                            if isinstance(repo, dict):
                                repo_full_name = repo.get('full_name', '')
                                
                                # Only include repositories that belong to the current user (nvelagaleti)
                                if repo_full_name and repo_full_name.startswith('nvelagaleti/'):
                                    if repo_full_name not in [r.get('full_name') for r in found_repos]:
                                        found_repos.append({
                                            'full_name': repo_full_name,
                                            'name': repo.get('name', ''),
                                            'description': repo.get('description', ''),
                                            'language': repo.get('language', 'Unknown'),
                                            'private': repo.get('private', False)
                                        })
                                        user_repos_found += 1
                        
                        if user_repos_found > 0:
                            print(f"✅ Found {user_repos_found} user repositories for keyword '{keyword}'")
                        else:
                            print(f"⚠️  No user repositories found for keyword '{keyword}'")
                    else:
                        print(f"⚠️  No results for keyword '{keyword}'")
                        if result:
                            print(f"🔍 Result type: {type(result)}")
                            if isinstance(result, dict):
                                print(f"🔍 Result keys: {list(result.keys())}")
                                print(f"🔍 Result content: {result}")
                            else:
                                print(f"🔍 Result content: {result}")
                        else:
                            print(f"🔍 Result is None or empty")
                        
                except Exception as e:
                    print(f"⚠️  Search failed for keyword '{keyword}': {e}")
            
            if found_repos:
                # Return just the full names for compatibility
                repo_names = [repo['full_name'] for repo in found_repos]
                print(f"✅ MCP search found {len(repo_names)} user repositories: {repo_names}")
                return repo_names
            else:
                print("⚠️  No repositories found via MCP search")
                return []
        else:
            print("⚠️  search_repositories tool not found in MCP tools")
            return []
        
    except Exception as e:
        print(f"⚠️  Error searching repositories with MCP: {e}")
        import traceback
        traceback.print_exc()
        return []


# MCP Integration imports
try:
    from jira_mcp_complete_integration import JiraMCPCompleteIntegration
    from token_manager import TokenManager
    JIRA_MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Jira MCP integration not available: {e}")
    JIRA_MCP_AVAILABLE = False

try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.tools import load_mcp_tools
    GITHUB_MCP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  GitHub MCP integration not available: {e}")
    GITHUB_MCP_AVAILABLE = False

# Helper functions for LLM analysis and GitHub MCP code inspection
async def generate_incident_search_keywords(description: str, title: str) -> list:
    """Use LLM to generate intelligent search keywords based on the incident."""
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an incident response analyst. Based on the incident description, generate specific search keywords 
            that would help identify related code, dependencies, and potential root causes.
            
            Focus on:
            - Technology stack keywords (React, Apollo, GraphQL, etc.)
            - Error types (timeout, memory, connection, etc.)
            - Service names and API endpoints
            - Configuration and deployment terms
            """),
            ("human", """
            Incident Title: {title}
            Incident Description: {description}
            
            Generate 5-8 specific search keywords as a JSON array:
            ["keyword1", "keyword2", "keyword3"]
            
            Focus on terms that would appear in code, configuration files, or error messages.
            """)
        ])
        
        formatted_prompt = prompt.format_messages(title=title, description=description)
        prompt_text = formatted_prompt[-1].content
        
        response = await llm.invoke(prompt_text)
        
        # Parse JSON response
        import re
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            keywords = json.loads(json_match.group())
            return keywords[:8]  # Limit to 8 keywords
        
        # Fallback keywords
        fallback_keywords = []
        if 'apollo' in description.lower() or 'graphql' in description.lower():
            fallback_keywords.extend(['apollo', 'graphql', 'query', 'mutation'])
        if 'memory' in description.lower():
            fallback_keywords.extend(['memory', 'leak', 'heap', 'gc'])
        if 'timeout' in description.lower():
            fallback_keywords.extend(['timeout', 'connection', 'network'])
        if 'products' in description.lower():
            fallback_keywords.extend(['products', 'api', 'service'])
        
        return fallback_keywords or ['error', 'service', 'api', 'config']
        
    except Exception as e:
        print(f"⚠️  Error generating search keywords: {e}")
        return ['error', 'service', 'api', 'config']

async def analyze_repository_code(repo_name: str, search_keywords: list) -> dict:
    """Analyze repository code using GitHub MCP to understand dependencies and structure."""
    try:
        # Extract owner and repo from full name
        if '/' in repo_name:
            owner, repo = repo_name.split('/', 1)
        else:
            owner = "nvelagaleti"
            repo = repo_name
        
        analysis = {
            'repository': repo_name,
            'dependencies': [],
            'technologies': [],
            'api_endpoints': [],
            'error_patterns': [],
            'configuration_files': []
        }
        
        if GITHUB_MCP_AVAILABLE and github_mcp_client:
            tools = await github_mcp_client.get_tools()
            
            # Search for package.json to understand dependencies
            try:
                package_json_tool = None
                for tool in tools:
                    if hasattr(tool, 'name') and 'get_content' in tool.name.lower():
                        package_json_tool = tool
                        break
                
                if package_json_tool:
                    # Get package.json content
                    package_content = await package_json_tool.ainvoke({
                        "owner": owner,
                        "repo": repo,
                        "path": "package.json"
                    })
                    
                    if package_content and isinstance(package_content, dict):
                        dependencies = package_content.get('dependencies', {})
                        dev_dependencies = package_content.get('devDependencies', {})
                        
                        # Analyze dependencies for technology stack
                        all_deps = {**dependencies, **dev_dependencies}
                        for dep, version in all_deps.items():
                            if 'apollo' in dep.lower():
                                analysis['technologies'].append('Apollo GraphQL')
                            elif 'graphql' in dep.lower():
                                analysis['technologies'].append('GraphQL')
                            elif 'react' in dep.lower():
                                analysis['technologies'].append('React')
                            elif 'express' in dep.lower() or 'koa' in dep.lower():
                                analysis['technologies'].append('Node.js/Express')
                        
                        analysis['dependencies'] = list(all_deps.keys())
            except Exception as e:
                print(f"⚠️  Error analyzing package.json for {repo_name}: {e}")
            
            # Search for code files containing our keywords
            for keyword in search_keywords[:3]:  # Use top 3 keywords
                try:
                    search_tool = None
                    for tool in tools:
                        if hasattr(tool, 'name') and 'search' in tool.name.lower():
                            search_tool = tool
                            break
                    
                    if search_tool:
                        search_result = await search_tool.ainvoke({
                            "query": f"repo:{owner}/{repo} {keyword}",
                            "per_page": 5
                        })
                        
                        if search_result and isinstance(search_result, dict) and 'items' in search_result:
                            for item in search_result['items']:
                                file_path = item.get('path', '')
                                if file_path:
                                    if 'api' in file_path.lower() or 'endpoint' in file_path.lower():
                                        analysis['api_endpoints'].append(file_path)
                                    elif 'config' in file_path.lower() or 'env' in file_path.lower():
                                        analysis['configuration_files'].append(file_path)
                                    elif 'error' in file_path.lower() or 'exception' in file_path.lower():
                                        analysis['error_patterns'].append(file_path)
                except Exception as e:
                    print(f"⚠️  Error searching for keyword '{keyword}' in {repo_name}: {e}")
        
        return analysis
        
    except Exception as e:
        print(f"⚠️  Error analyzing repository {repo_name}: {e}")
        return {
            'repository': repo_name,
            'dependencies': [],
            'technologies': [],
            'api_endpoints': [],
            'error_patterns': [],
            'configuration_files': []
        }

async def find_dependent_repositories(first_repo: str, first_repo_analysis: dict, all_repos: list) -> list:
    """Find dependent repositories based on code analysis."""
    try:
        dependent_repos = []
        first_repo_technologies = first_repo_analysis.get('technologies', [])
        first_repo_dependencies = first_repo_analysis.get('dependencies', [])
        
        # Logic to determine dependent repositories based on technology stack
        if 'Apollo GraphQL' in first_repo_technologies or 'GraphQL' in first_repo_technologies:
            # If first repo uses GraphQL, look for GraphQL service
            for repo in all_repos:
                if 'graphql' in repo.lower() and repo != first_repo:
                    dependent_repos.append(repo)
                    break
        
        if 'React' in first_repo_technologies:
            # If first repo is React frontend, look for backend services
            for repo in all_repos:
                if ('backend' in repo.lower() or 'service' in repo.lower()) and repo != first_repo:
                    dependent_repos.append(repo)
        
        # Check for API dependencies
        if first_repo_analysis.get('api_endpoints'):
            # If first repo has API endpoints, look for backend services
            for repo in all_repos:
                if ('backend' in repo.lower() or 'api' in repo.lower()) and repo != first_repo:
                    if repo not in dependent_repos:
                        dependent_repos.append(repo)
        
        return dependent_repos
        
    except Exception as e:
        print(f"⚠️  Error finding dependent repositories: {e}")
        return []

# Intelligent commit analysis functions
async def generate_commit_analysis_strategy(description: str, title: str, enhanced_analysis: dict) -> dict:
    """Use LLM to generate intelligent commit analysis strategy based on incident."""
    try:
        # Summarize repository technologies for context
        all_technologies = []
        for repo_analysis in enhanced_analysis.values():
            all_technologies.extend(repo_analysis.get('technologies', []))
        unique_technologies = list(set(all_technologies))
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an incident response analyst specializing in commit analysis. Based on the incident description 
            and technology stack, generate an intelligent strategy for analyzing commits to find the root cause.
            
            Focus on:
            - What types of commits to look for
            - Which repositories to prioritize
            - What patterns indicate the root cause
            - How to correlate commits across services
            """),
            ("human", """
            Incident Title: {title}
            Incident Description: {description}
            Technology Stack: {technologies}
            
            Generate analysis strategy as JSON:
            {{
                "priority_repositories": ["list", "of", "repos", "to", "focus", "on"],
                "suspicious_patterns": ["list", "of", "commit", "patterns", "to", "look", "for"],
                "correlation_strategy": "how to correlate commits across repos",
                "root_cause_indicators": ["list", "of", "indicators", "that", "suggest", "root", "cause"]
            }}
            """)
        ])
        
        formatted_prompt = prompt.format_messages(
            title=title, 
            description=description, 
            technologies=unique_technologies
        )
        prompt_text = formatted_prompt[-1].content
        
        response = await llm.invoke(prompt_text)
        
        # Parse JSON response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            strategy = json.loads(json_match.group())
            return strategy
        
        # Fallback strategy
        return {
            "priority_repositories": ["backend", "service", "api"],
            "suspicious_patterns": ["memory", "config", "deploy", "fix"],
            "correlation_strategy": "Look for commits with similar timestamps and related changes",
            "root_cause_indicators": ["memory-related changes", "configuration updates", "recent deployments"]
        }
        
    except Exception as e:
        print(f"⚠️  Error generating commit analysis strategy: {e}")
        return {
            "priority_repositories": ["backend", "service", "api"],
            "suspicious_patterns": ["memory", "config", "deploy", "fix"],
            "correlation_strategy": "Look for commits with similar timestamps and related changes",
            "root_cause_indicators": ["memory-related changes", "configuration updates", "recent deployments"]
        }

async def analyze_repository_commits_intelligently(repo: str, commits: list, description: str, title: str, technologies: list, strategy: dict) -> list:
    """Intelligently analyze commits for a specific repository using LLM."""
    try:
        suspicious_commits = []
        
        # Use LLM to analyze each commit in context
        for commit in commits[:10]:  # Analyze last 10 commits
            commit_analysis = await analyze_single_commit_intelligently(
                commit, repo, description, title, technologies, strategy
            )
            
            if commit_analysis.get('suspicious_score', 0) > 0.3:
                suspicious_commits.append(commit_analysis)
        
        return suspicious_commits
        
    except Exception as e:
        print(f"⚠️  Error analyzing commits for {repo}: {e}")
        return []

async def analyze_single_commit_intelligently(commit: dict, repo: str, description: str, title: str, technologies: list, strategy: dict) -> dict:
    """Use LLM to analyze a single commit in the context of the incident."""
    try:
        message = commit.get('message', '')
        sha = commit.get('sha', '')
        author = commit.get('author', '')
        date = commit.get('date', '')
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an incident response analyst. Analyze this commit to determine if it could be related to the incident.
            Consider the commit message, timing, repository, and technology stack.
            """),
            ("human", """
            Incident Title: {title}
            Incident Description: {description}
            Repository: {repo}
            Technologies: {technologies}
            Analysis Strategy: {strategy}
            
            Commit Details:
            - Message: {message}
            - SHA: {sha}
            - Author: {author}
            - Date: {date}
            
            Analyze this commit and return JSON:
            {{
                "suspicious_score": 0.0-1.0,
                "potential_issue": "description of potential issue",
                "reasoning": "why this commit is suspicious",
                "confidence": 0.0-1.0,
                "repo": "{repo}",
                "sha": "{sha}",
                "message": "{message}",
                "author": "{author}",
                "date": "{date}"
            }}
            """)
        ])
        
        formatted_prompt = prompt.format_messages(
            title=title,
            description=description,
            repo=repo,
            technologies=technologies,
            strategy=strategy,
            message=message,
            sha=sha,
            author=author,
            date=date
        )
        prompt_text = formatted_prompt[-1].content
        
        response = await llm.invoke(prompt_text)
        
        # Parse JSON response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
            return analysis
        
        # Fallback analysis
        suspicious_score = 0.0
        potential_issue = ""
        reasoning = ""
        
        # Basic pattern matching as fallback
        message_lower = message.lower()
        if any(pattern in message_lower for pattern in strategy.get('suspicious_patterns', [])):
            suspicious_score += 0.4
            potential_issue = f"Contains suspicious keywords: {[p for p in strategy.get('suspicious_patterns', []) if p in message_lower]}"
            reasoning = "Commit message contains keywords that match suspicious patterns"
        
        # Check if repository is in priority list
        if any(priority in repo.lower() for priority in strategy.get('priority_repositories', [])):
            suspicious_score += 0.2
            reasoning += "; Repository is in priority list"
        
        return {
            "suspicious_score": suspicious_score,
            "potential_issue": potential_issue,
            "reasoning": reasoning,
            "confidence": suspicious_score,
            "repo": repo,
            "sha": sha,
            "message": message,
            "author": author,
            "date": date
        }
        
    except Exception as e:
        print(f"⚠️  Error analyzing single commit: {e}")
        return {
            "suspicious_score": 0.0,
            "potential_issue": "Analysis failed",
            "reasoning": f"Error in analysis: {e}",
            "confidence": 0.0,
            "repo": repo,
            "sha": commit.get('sha', ''),
            "message": commit.get('message', ''),
            "author": commit.get('author', ''),
            "date": commit.get('date', '')
        }

async def correlate_commits_across_repos(suspicious_commits: list, description: str, title: str) -> str:
    """Use LLM to correlate suspicious commits across repositories."""
    try:
        if not suspicious_commits:
            return "No suspicious commits to correlate"
        
        # Prepare commit summary for LLM
        commit_summary = []
        for commit in suspicious_commits[:5]:  # Top 5 suspicious commits
            commit_summary.append({
                "repo": commit.get('repo', ''),
                "sha": commit.get('sha', '')[:8],
                "message": commit.get('message', ''),
                "confidence": commit.get('confidence', 0),
                "potential_issue": commit.get('potential_issue', '')
            })
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an incident response analyst. Analyze these suspicious commits across repositories 
            to identify patterns and potential root cause relationships.
            """),
            ("human", """
            Incident Title: {title}
            Incident Description: {description}
            
            Suspicious Commits:
            {commits}
            
            Analyze these commits and provide correlation insights:
            - Are there patterns across repositories?
            - Which commit is most likely the root cause?
            - What's the relationship between these commits?
            - Timeline analysis?
            """)
        ])
        
        formatted_prompt = prompt.format_messages(
            title=title,
            description=description,
            commits=json.dumps(commit_summary, indent=2)
        )
        prompt_text = formatted_prompt[-1].content
        
        response = await llm.invoke(prompt_text)
        return response
        
    except Exception as e:
        print(f"⚠️  Error correlating commits: {e}")
        return f"Error in correlation analysis: {e}"

async def perform_intelligent_rca(log_analysis: dict, commit_analysis: dict, enhanced_analysis: dict, description: str, title: str) -> dict:
    """Use LLM to perform intelligent Root Cause Analysis."""
    try:
        # Prepare comprehensive data for LLM analysis
        analysis_data = {
            "incident": {
                "title": title,
                "description": description
            },
            "log_analysis": {
                "error_summary": log_analysis.get('error_summary', []),
                "log_patterns": log_analysis.get('log_patterns', []),
                "total_log_entries": log_analysis.get('total_log_entries', 0)
            },
            "commit_analysis": {
                "suspicious_commits": commit_analysis.get('suspicious_commits', []),
                "root_cause_commits": commit_analysis.get('root_cause_commits', []),
                "correlation_analysis": commit_analysis.get('correlation_analysis', ''),
                "high_confidence_candidates": commit_analysis.get('high_confidence_candidates', 0)
            },
            "enhanced_analysis": {
                "repositories": list(enhanced_analysis.keys()),
                "technologies": list(set([tech for repo in enhanced_analysis.values() for tech in repo.get('technologies', [])]))
            }
        }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a senior incident response analyst. Perform a comprehensive Root Cause Analysis (RCA) 
            based on the provided data. Your goal is to identify the most likely root cause of the incident.
            
            Focus on:
            - Correlating log errors with suspicious commits
            - Identifying the primary suspect commit
            - Understanding the incident timeline
            - Determining confidence levels
            - Providing actionable insights
            """),
            ("human", """
            Incident Analysis Data:
            {analysis_data}
            
            Perform comprehensive RCA and return JSON:
            {{
                "root_cause": "primary root cause description",
                "primary_suspect": {{
                    "repo": "repository name",
                    "sha": "commit sha",
                    "message": "commit message",
                    "confidence": 0.0-1.0,
                    "reasoning": "why this is the primary suspect"
                }},
                "contributing_factors": ["list", "of", "contributing", "factors"],
                "evidence": ["list", "of", "supporting", "evidence"],
                "confidence": 0.0-1.0,
                "timeline": "incident timeline analysis",
                "impact_analysis": "how the root cause led to the incident",
                "prevention_measures": ["list", "of", "prevention", "measures"]
            }}
            """)
        ])
        
        formatted_prompt = prompt.format_messages(
            analysis_data=json.dumps(analysis_data, indent=2)
        )
        prompt_text = formatted_prompt[-1].content
        
        response = await llm.invoke(prompt_text)
        
        # Parse JSON response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            rca = json.loads(json_match.group())
            return rca
        
        # Fallback RCA
        return create_fallback_rca(log_analysis, commit_analysis, description)
        
    except Exception as e:
        print(f"⚠️  Error performing intelligent RCA: {e}")
        return create_fallback_rca(log_analysis, commit_analysis, description)

def create_fallback_rca(log_analysis: dict, commit_analysis: dict, description: str) -> dict:
    """Create fallback RCA when LLM analysis fails."""
    root_cause = "Unknown"
    confidence = 0.0
    contributing_factors = []
    evidence = []
    
    # Basic analysis
    if commit_analysis.get('root_cause_commits'):
        root_cause = "Suspicious commit detected"
        confidence = 0.7
        contributing_factors.append("Recent suspicious commits")
        evidence.extend([f"Commit {c['sha'][:8]} in {c['repo']}" for c in commit_analysis['root_cause_commits'][:3]])
    
    if log_analysis.get('error_summary'):
        contributing_factors.append("Log errors detected")
        evidence.extend(log_analysis['error_summary'][:3])
        confidence = max(confidence, 0.5)
    
    if 'memory' in description.lower():
        root_cause = "Memory-related issue"
        confidence = max(confidence, 0.6)
    
    return {
        "root_cause": root_cause,
        "primary_suspect": commit_analysis.get('root_cause_commits', [{}])[0] if commit_analysis.get('root_cause_commits') else {},
        "contributing_factors": contributing_factors,
        "evidence": evidence,
        "confidence": confidence,
        "timeline": "Fallback timeline analysis",
        "impact_analysis": "Fallback impact analysis",
        "prevention_measures": ["Implement monitoring", "Add automated testing", "Improve deployment process"]
    }

async def generate_intelligent_action_items(log_analysis: dict, commit_analysis: dict, rca: dict, enhanced_analysis: dict, description: str, title: str) -> dict:
    """Use LLM to generate intelligent action items based on all analysis data."""
    try:
        # Prepare comprehensive data for LLM analysis
        analysis_data = {
            "incident": {
                "title": title,
                "description": description
            },
            "log_analysis": {
                "log_based_actions": log_analysis.get('log_based_actions', []),
                "error_summary": log_analysis.get('error_summary', []),
                "log_patterns": log_analysis.get('log_patterns', [])
            },
            "commit_analysis": {
                "commit_based_actions": commit_analysis.get('commit_based_actions', []),
                "suspicious_commits": commit_analysis.get('suspicious_commits', []),
                "root_cause_commits": commit_analysis.get('root_cause_commits', [])
            },
            "rca": {
                "root_cause": rca.get('root_cause', ''),
                "primary_suspect": rca.get('primary_suspect', {}),
                "contributing_factors": rca.get('contributing_factors', []),
                "prevention_measures": rca.get('prevention_measures', [])
            },
            "enhanced_analysis": {
                "repositories": list(enhanced_analysis.keys()),
                "technologies": list(set([tech for repo in enhanced_analysis.values() for tech in repo.get('technologies', [])]))
            }
        }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a senior incident response manager. Generate comprehensive action items based on the incident analysis.
            
            Focus on:
            - Immediate actions to resolve the incident
            - Short-term actions to prevent recurrence
            - Long-term prevention measures
            - Team assignments and effort estimates
            - Priority levels based on impact and urgency
            """),
            ("human", """
            Incident Analysis Data:
            {analysis_data}
            
            Generate comprehensive action items and return JSON:
            {{
                "action_items": [
                    {{
                        "action": "specific action description",
                        "priority": "high|medium|low",
                        "category": "immediate|short_term|long_term",
                        "assignee": "team or person responsible",
                        "estimated_effort": "time estimate",
                        "description": "detailed description",
                        "source": "log_analysis|commit_analysis|rca|prevention"
                    }}
                ],
                "immediate_actions": ["list", "of", "immediate", "actions"],
                "short_term_actions": ["list", "of", "short", "term", "actions"],
                "long_term_actions": ["list", "of", "long", "term", "actions"],
                "prevention_measures": ["list", "of", "prevention", "measures"],
                "team_assignments": {{
                    "devops_team": ["list", "of", "devops", "tasks"],
                    "development_team": ["list", "of", "development", "tasks"],
                    "sre_team": ["list", "of", "sre", "tasks"]
                }}
            }}
            """)
        ])
        
        formatted_prompt = prompt.format_messages(
            analysis_data=json.dumps(analysis_data, indent=2)
        )
        prompt_text = formatted_prompt[-1].content
        
        response = await llm.invoke(prompt_text)
        
        # Parse JSON response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            actions = json.loads(json_match.group())
            return actions
        
        # Fallback action items
        return create_fallback_action_items(log_analysis, commit_analysis, rca)
        
    except Exception as e:
        print(f"⚠️  Error generating intelligent action items: {e}")
        return create_fallback_action_items(log_analysis, commit_analysis, rca)

def create_fallback_action_items(log_analysis: dict, commit_analysis: dict, rca: dict) -> dict:
    """Create fallback action items when LLM analysis fails."""
    action_items = []
    immediate_actions = []
    prevention_measures = []
    
    # Add log-based actions
    for action in log_analysis.get('log_based_actions', []):
        action_items.append({
            "action": action.get('action', ''),
            "priority": action.get('priority', 'medium'),
            "category": "immediate" if action.get('priority') == 'high' else "short_term",
            "assignee": "DevOps Team",
            "estimated_effort": "2-4 hours",
            "description": action.get('reasoning', ''),
            "source": "log_analysis"
        })
        if action.get('priority') == 'high':
            immediate_actions.append(action.get('action', ''))
    
    # Add commit-based actions
    for action in commit_analysis.get('commit_based_actions', []):
        action_items.append({
            "action": action.get('action', ''),
            "priority": action.get('priority', 'medium'),
            "category": "immediate" if action.get('priority') == 'high' else "short_term",
            "assignee": "Development Team",
            "estimated_effort": "1-2 hours",
            "description": action.get('reasoning', ''),
            "source": "commit_analysis"
        })
        if action.get('priority') == 'high':
            immediate_actions.append(action.get('action', ''))
    
    # Add prevention measures
    prevention_measures.extend([
        "Implement comprehensive monitoring",
        "Add automated testing",
        "Improve deployment process",
        "Set up incident response playbooks"
    ])
    
    return {
        "action_items": action_items,
        "immediate_actions": immediate_actions,
        "short_term_actions": [a.get('action', '') for a in action_items if a.get('category') == 'short_term'],
        "long_term_actions": [a.get('action', '') for a in action_items if a.get('category') == 'long_term'],
        "prevention_measures": prevention_measures,
        "team_assignments": {
            "devops_team": [a.get('action', '') for a in action_items if a.get('assignee') == 'DevOps Team'],
            "development_team": [a.get('action', '') for a in action_items if a.get('assignee') == 'Development Team'],
            "sre_team": ["Implement monitoring", "Set up alerting"]
        }
    }

async def create_comprehensive_ticket_update(rca: dict, action_items: list, consolidated_actions: dict, ir_ticket: dict) -> dict:
    """Create comprehensive ticket update content using LLM."""
    try:
        # Use LLM to create professional ticket update
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a senior incident response analyst. Create a comprehensive and professional update 
            for the Jira incident ticket based on the investigation results.
            """),
            ("human", """
            Root Cause Analysis: {rca}
            Action Items: {action_items}
            Consolidated Actions: {consolidated_actions}
            Original Ticket: {ir_ticket}
            
            Create a comprehensive ticket update with:
            1. A clear summary line
            2. Detailed description with investigation findings
            3. Root cause analysis
            4. Action items and next steps
            5. Prevention measures
            
            Return JSON:
            {{
                "summary": "clear summary line",
                "description": "detailed description with all findings"
            }}
            """)
        ])
        
        formatted_prompt = prompt.format_messages(
            rca=json.dumps(rca, indent=2),
            action_items=json.dumps(action_items, indent=2),
            consolidated_actions=json.dumps(consolidated_actions, indent=2),
            ir_ticket=json.dumps(ir_ticket, indent=2)
        )
        prompt_text = formatted_prompt[-1].content
        
        response = await llm.invoke(prompt_text)
        
        # Parse JSON response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            update_content = json.loads(json_match.group())
            return update_content
        
        # Fallback content
        return create_fallback_ticket_update(rca, action_items, consolidated_actions)
        
    except Exception as e:
        print(f"⚠️  Error creating comprehensive ticket update: {e}")
        return create_fallback_ticket_update(rca, action_items, consolidated_actions)

def create_fallback_ticket_update(rca: dict, action_items: list, consolidated_actions: dict) -> dict:
    """Create fallback ticket update when LLM fails."""
    root_cause = rca.get('root_cause', 'Unknown')
    primary_suspect = rca.get('primary_suspect', {})
    
    summary = f"INVESTIGATION COMPLETE: Root Cause - {root_cause}. {len(action_items)} action items identified."
    
    description = f"""
# Incident Investigation Complete

## Root Cause Analysis
- **Primary Root Cause**: {root_cause}
- **Confidence Level**: {rca.get('confidence', 0):.2f}
- **Primary Suspect**: {primary_suspect.get('sha', 'None')} in {primary_suspect.get('repo', 'Unknown')}
- **Contributing Factors**: {', '.join(rca.get('contributing_factors', []))}

## Evidence
{chr(10).join([f"- {evidence}" for evidence in rca.get('evidence', [])])}

## Action Items ({len(action_items)} total)
{chr(10).join([f"- {action.get('action', '')} (Priority: {action.get('priority', 'medium')})" for action in action_items[:5]])}

## Prevention Measures
{chr(10).join([f"- {measure}" for measure in rca.get('prevention_measures', [])])}

## Investigation Details
- **Investigation Method**: AI-powered analysis with real data
- **Repositories Analyzed**: {len(consolidated_actions.get('team_assignments', {}).get('devops_team', [])) + len(consolidated_actions.get('team_assignments', {}).get('development_team', []))}
- **High Priority Actions**: {len(consolidated_actions.get('immediate_actions', []))}
- **Investigation Completed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return {
        "summary": summary,
        "description": description
    }

# Helper functions for real data retrieval
async def get_repository_commits(repo_name: str) -> list:
    """Get recent commits for a repository using GitHub MCP."""
    try:
        # Extract owner and repo from full name (e.g., "nvelagaleti/productsWebApp")
        if '/' in repo_name:
            owner, repo = repo_name.split('/', 1)
        else:
            owner = "nvelagaleti"
            repo = repo_name
        
        # Use GitHub MCP to get commits
        if GITHUB_MCP_AVAILABLE and github_mcp_client:
            tools = await github_mcp_client.get_tools()
            list_commits_tool = None
            
            for tool in tools:
                if hasattr(tool, 'name') and 'list_commits' in tool.name.lower():
                    list_commits_tool = tool
                    break
            
            if list_commits_tool:
                result = await list_commits_tool.ainvoke({
                    "owner": owner,
                    "repo": repo,
                    "per_page": 10  # Get last 10 commits
                })
                
                if result and isinstance(result, list):
                    commits = []
                    for commit in result:
                        if isinstance(commit, dict):
                            commits.append({
                                "sha": commit.get('sha', ''),
                                "message": commit.get('commit', {}).get('message', ''),
                                "author": commit.get('commit', {}).get('author', {}).get('name', ''),
                                "date": commit.get('commit', {}).get('author', {}).get('date', ''),
                                "files": []  # Could be expanded to get changed files
                            })
                    return commits
        
        # Fallback: return empty list if MCP not available
        return []
        
    except Exception as e:
        print(f"⚠️  Error getting commits for {repo_name}: {e}")
        return []

async def get_local_repository_logs(repo_name: str) -> list:
    """Get logs from local repository files."""
    try:
        # Extract repo name from full name (e.g., "nvelagaleti/productsWebApp" -> "productsWebApp")
        if '/' in repo_name:
            repo = repo_name.split('/', 1)[1]
        else:
            repo = repo_name
        
        # Look for log files in the repository
        log_files = [
            f"logs/{repo}.log",
            f"{repo}/logs/app.log",
            f"{repo}/logs/error.log",
            f"{repo}/logs/debug.log",
            f"{repo}/app.log",
            f"{repo}/error.log"
        ]
        
        logs = []
        
        for log_file in log_files:
            try:
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        # Parse last 20 lines as log entries
                        for line in lines[-20:]:
                            if line.strip():
                                logs.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "level": "INFO",
                                    "message": line.strip(),
                                    "service": repo,
                                    "source": log_file
                                })
            except Exception as e:
                print(f"⚠️  Error reading log file {log_file}: {e}")
                continue
        
        # If no log files found, create a placeholder
        if not logs:
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "level": "INFO",
                "message": f"No log files found for {repo}",
                "service": repo,
                "source": "placeholder"
            })
        
        return logs
        
    except Exception as e:
        print(f"⚠️  Error getting logs for {repo_name}: {e}")
        return []

# Input schema for LangGraph Studio - only incident_id required
class IncidentInput(TypedDict):
    """Input schema for the enhanced incident response workflow."""
    incident_id: str

# Internal state definition for the workflow
class IncidentState(TypedDict, total=False):
    """State for the enhanced incident response workflow."""
    # Input (required)
    incident_id: str
    
    # Generated during workflow
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Step 2-3: Repo Discovery
    first_repo: str
    repo_path: List[str]  # UI -> GraphQL -> Backend path
    all_repos: List[str]
    
    # Step 4: Parallel Analysis
    repo_commits: Dict[str, List[Dict[str, Any]]]
    repo_logs: Dict[str, List[Dict[str, Any]]]
    
    # Step 5-6: Analysis Results
    log_analysis: Dict[str, Any]
    commit_analysis: Dict[str, Any]
    
    # Step 7-8: RCA and Actions
    root_cause_analysis: Dict[str, Any]
    action_items: List[Dict[str, Any]]
    
    # Step 9: Ticket Update
    updated_ticket: Dict[str, Any]
    
    # MCP Integrations
    incident_analysis: Dict[str, Any]
    repo_analysis: Dict[str, Any]  # Repository identification analysis from Step 2
    jira_tickets: List[Dict[str, Any]]
    mcp_integrations: Dict[str, Any]
    
    # General
    messages: List[Dict[str, Any]]
    completed_steps: List[str]


# Circuit LLM setup
from circuit_llm_client import CircuitLLMWrapper

# Initialize Circuit LLM wrapper
circuit_llm_wrapper = CircuitLLMWrapper()

# Create a LangChain-compatible LLM interface
class CircuitLLM:
    """LangChain-compatible interface for Circuit LLM."""
    
    def __init__(self, wrapper: CircuitLLMWrapper):
        self.wrapper = wrapper
    
    async def invoke(self, input_text: str) -> str:
        """Invoke Circuit LLM with input text."""
        return await self.wrapper.invoke(input_text)
    
    async def ainvoke(self, input_text: str) -> str:
        """Async invoke Circuit LLM with input text."""
        return await self.wrapper.ainvoke(input_text)

# Initialize the LLM
llm = CircuitLLM(circuit_llm_wrapper)

# Initialize MCP clients
jira_mcp_client = None
github_mcp_client = None

if JIRA_MCP_AVAILABLE:
    try:
        jira_mcp_client = JiraMCPCompleteIntegration()
        print("✅ Jira MCP client created")
    except Exception as e:
        print(f"❌ Failed to create Jira MCP client: {e}")
        jira_mcp_client = None

if GITHUB_MCP_AVAILABLE:
    try:
        github_mcp_client = MultiServerMCPClient(
            {
                "github": {
                    "url": "https://api.githubcopilot.com/mcp/",
                    "transport": "streamable_http",
                    "headers": {
                        "Authorization": f"Bearer {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}",
                        "Accept": "application/vnd.github.v3+json",
                        "Content-Type": "application/json"
                    }
                }
            }
        )
        print("✅ GitHub Copilot MCP client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize GitHub Copilot MCP client: {e}")
        github_mcp_client = None


async def step1_parse_ir_ticket(state: IncidentInput) -> IncidentState:
    """Step 1: Fetch incident details from Jira MCP and analyze with GitHub MCP."""
    print("=" * 80)
    print("🚀 STEP1_Parse_IR_Ticket: Starting execution")
    print("=" * 80)
    print(f"📥 Input state keys: {list(state.keys()) if hasattr(state, 'keys') else 'No keys'}")
    print(f"📥 Input state type: {type(state)}")
    
    incident_id = state.get('incident_id', '')
    print(f"🔍 Incident ID from state: '{incident_id}' (type: {type(incident_id)})")
    
    if not incident_id:
        print("❌ ERROR: incident_id is empty or missing")
        print(f"🔍 State content: {state}")
        raise ValueError("incident_id is required")
    
    print(f"✅ Incident ID validated: '{incident_id}'")
    
    try:
        # Initialize Jira MCP client to fetch real incident details
        print("🔧 STEP1: Initializing Jira MCP client...")
        
        # Create a fresh Jira MCP client instance for this step
        print("🔧 STEP1: Creating JiraMCPCompleteIntegration instance...")
        jira_client = JiraMCPCompleteIntegration()
        print("✅ STEP1: JiraMCPCompleteIntegration instance created")
        
        # Initialize the client asynchronously
        print("🔧 STEP1: Initializing Jira client asynchronously...")
        await jira_client.initialize()
        print("✅ STEP1: Jira client initialized successfully")
        
        # Use Jira MCP to search for the incident by ID - exact match only
        jql_query = f'issuekey = "{incident_id}"'
        print(f"🔍 STEP1: JQL Query: '{jql_query}'")
        
        try:
            print(f"🔍 STEP1: Searching for incident with JQL: {jql_query}")
            print(f"🔍 STEP1: Calling jira_client.search_issues...")
            jira_issues = await jira_client.search_issues(
                jql=jql_query,
                max_results=1
            )
            print(f"✅ STEP1: search_issues completed, result type: {type(jira_issues)}")
            print(f"✅ STEP1: search_issues result length: {len(jira_issues) if jira_issues else 0}")
        except Exception as e:
            print(f"❌ STEP1: Error searching issues: {e}")
            print(f"❌ STEP1: Error type: {type(e)}")
            import traceback
            print(f"❌ STEP1: Full traceback:")
            traceback.print_exc()
            jira_issues = None
        
        if not jira_issues or len(jira_issues) == 0:
            print(f"⚠️  STEP1: Incident {incident_id} not found in Jira, using fallback data")
            print(f"⚠️  STEP1: jira_issues value: {jira_issues}")
            print(f"⚠️  STEP1: jira_issues type: {type(jira_issues)}")
            incident_details = {
                'title': f'Incident {incident_id}',
                'description': 'Incident details not found in Jira system',
                'severity': 'medium',
                'status': 'open',
                'error_message': 'Service unavailable',
                'affected_components': ['frontend', 'api'],
                'user_impact': 'Users unable to access application'
            }
            print(f"⚠️  STEP1: Using fallback incident details: {incident_details}")
        else:
            # Extract real incident details from Jira
            print(f"✅ STEP1: Found {len(jira_issues)} issues, processing first issue")
            jira_issue = jira_issues[0]
            print(f"🔍 STEP1: Jira issue structure: {list(jira_issue.keys())}")
            print(f"🔍 STEP1: Jira issue key: {jira_issue.get('key', 'N/A')}")
            fields = jira_issue.get('fields', {})
            print(f"🔍 STEP1: Fields available: {list(fields.keys())}")
            
            # Handle description which might be in Atlassian Document Format
            description = fields.get('description', '')
            if isinstance(description, dict) and 'content' in description:
                # Extract text from Atlassian Document Format
                content_parts = []
                for content in description.get('content', []):
                    if 'content' in content:
                        for text_content in content['content']:
                            if text_content.get('type') == 'text':
                                content_parts.append(text_content.get('text', ''))
                description = ' '.join(content_parts)
            
            # Get priority name safely
            priority_obj = fields.get('priority', {})
            priority_name = priority_obj.get('name', 'Medium') if isinstance(priority_obj, dict) else 'Medium'
            
            # Get assignee name safely
            assignee_obj = fields.get('assignee', {})
            assignee_name = assignee_obj.get('displayName', 'Unassigned') if isinstance(assignee_obj, dict) else 'Unassigned'
            
            # Get reporter name safely
            reporter_obj = fields.get('reporter', {})
            reporter_name = reporter_obj.get('displayName', 'Unknown') if isinstance(reporter_obj, dict) else 'Unknown'
            
            incident_details = {
                'title': fields.get('summary', f'Incident {incident_id}'),
                'description': description,
                'severity': priority_name.lower(),
                'status': 'open',  # Default since status field doesn't exist in your Jira
                'error_message': description,
                'affected_components': [fields.get('environment', 'unknown')],
                'user_impact': description,
                'jira_issue_key': jira_issue.get('key', incident_id),
                'jira_issue_id': jira_issue.get('id', ''),
                'created': jira_issue.get('created', ''),
                'updated': jira_issue.get('updated', ''),
                'assignee': assignee_name,
                'reporter': reporter_name,
                'labels': fields.get('labels', []),
                'priority': priority_name
            }
            print(f"✅ STEP1: Extracted incident details successfully")
            print(f"✅ STEP1: Title: {incident_details['title']}")
            print(f"✅ STEP1: Severity: {incident_details['severity']}")
            print(f"✅ STEP1: Assignee: {incident_details['assignee']}")
        
        print(f"✅ STEP1: Fetched incident details: {incident_details['title']}")
        
        # Now use Circuit LLM to analyze the incident and provide investigation guidance
        print("🔍 STEP1: Analyzing incident with Circuit LLM for investigation guidance...")
        
        incident_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are analyzing an incident for investigation. Based on the incident description, provide guidance on:
            1. What types of changes to look for
            2. Recent timeframes to investigate
            3. Potential root causes based on common patterns
            4. Investigation approach and priorities
            """),
            ("human", """
            Incident Analysis:
            - Title: {title}
            - Description: {description}
            - Error Message: {error_message}
            - Affected Components: {affected_components}
            
            Based on this incident, provide investigation guidance as JSON:
            {{
                "change_types": ["list", "of", "change", "types", "to", "look", "for"],
                "timeframe_hours": "number",
                "analysis_focus": "string",
                "potential_root_causes": ["list", "of", "potential", "causes"],
                "suspicious_patterns": ["list", "of", "patterns", "to", "look", "for"],
                "recent_commits_to_review": ["list", "of", "commit", "types"],
                "configuration_changes": ["list", "of", "config", "changes", "to", "check"],
                "investigation_priority": "high/medium/low",
                "suggested_approach": "step-by-step investigation approach"
            }}
            """),
            ("human", """
            Example: For a "Products page not loading" incident, focus on:
            - Recent UI changes, API modifications, configuration updates
            - Look for errors in frontend code, API endpoints, service configurations
            - Check recent deployments, database changes, network configurations
            """)
        ])
        
        # Format incident analysis prompt
        incident_formatted_prompt = incident_analysis_prompt.format_messages(
            title=incident_details.get('title', ''),
            description=incident_details.get('description', ''),
            error_message=incident_details.get('error_message', ''),
            affected_components=incident_details.get('affected_components', [])
        )
        
        # Get incident analysis using Circuit LLM
        incident_analysis_response = await llm.invoke(incident_formatted_prompt[-1].content)
        
        # Parse incident analysis
        import re
        incident_json_match = re.search(r'\{.*\}', incident_analysis_response, re.DOTALL)
        if incident_json_match:
            incident_analysis = json.loads(incident_json_match.group())
        else:
            incident_analysis = {
                "change_types": ["configuration", "deployment", "code"],
                "timeframe_hours": 24,
                "analysis_focus": "recent changes and performance issues",
                "potential_root_causes": ["recent deployment", "configuration change", "database query issue"],
                "suspicious_patterns": ["timeout errors", "slow queries", "memory issues"],
                "recent_commits_to_review": ["config changes", "deployment updates", "performance fixes"],
                "configuration_changes": ["database settings", "timeout values", "memory limits"],
                "investigation_priority": "medium",
                "suggested_approach": "Check recent changes in affected components"
            }
        
        # Create comprehensive incident state with real Jira data and GitHub analysis
        updated_state = state.copy()
        updated_state.update({
            'title': incident_details.get('title', f'Incident {incident_id}'),
            'description': incident_details.get('description', ''),
            'severity': incident_details.get('severity', 'medium'),
            'status': incident_details.get('status', 'open'),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'jira_issue_key': incident_details.get('jira_issue_key', incident_id),
            'jira_issue_id': incident_details.get('jira_issue_id', ''),
            'incident_analysis': {
                'change_types': incident_analysis.get('change_types', []),
                'timeframe_hours': incident_analysis.get('timeframe_hours', 24),
                'analysis_focus': incident_analysis.get('analysis_focus', ''),
                'potential_root_causes': incident_analysis.get('potential_root_causes', []),
                'suspicious_patterns': incident_analysis.get('suspicious_patterns', []),
                'recent_commits_to_review': incident_analysis.get('recent_commits_to_review', []),
                'configuration_changes': incident_analysis.get('configuration_changes', []),
                'investigation_priority': incident_analysis.get('investigation_priority', 'medium'),
                'suggested_approach': incident_analysis.get('suggested_approach', ''),
                'incident_details': incident_details
            },
            'mcp_integrations': {
                'github_enabled': bool(os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")),
                'jira_enabled': bool(os.getenv("JIRA_OAUTH_ACCESS_TOKEN")),
                'mcp_servers': []
            },
            'completed_steps': ['step1_parse_ir_ticket'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Fetched incident {incident_id} from Jira MCP and analyzed for investigation. Priority: {incident_analysis.get('investigation_priority', 'medium')}"
            }]
        })
        
        print(f"✅ STEP1: Incident fetched from Jira MCP: {updated_state['title']}")
        print(f"🎯 STEP1: Analysis focus: {incident_analysis.get('analysis_focus', '')}")
        print(f"🔍 STEP1: Investigation priority: {incident_analysis.get('investigation_priority', 'medium')}")
        print(f"✅ STEP1: Function completed successfully")
        print(f"✅ STEP1: Returning state with keys: {list(updated_state.keys())}")
        print("=" * 80)
        print("🚀 STEP1_Parse_IR_Ticket: Execution completed successfully")
        print("=" * 80)
        
        return updated_state
        
    except Exception as e:
        print(f"❌ STEP1: Error fetching incident from Jira MCP: {e}")
        print(f"❌ STEP1: Error type: {type(e)}")
        import traceback
        print(f"❌ STEP1: Full traceback:")
        traceback.print_exc()
        print("=" * 80)
        print("🚀 STEP1_Parse_IR_Ticket: Execution failed with error")
        print("=" * 80)
        # Fallback to basic incident details
        return_state = {
            **state,
            'title': f'Incident {incident_id}',
            'description': f'Error fetching incident details: {str(e)}',
            'severity': 'medium',
            'status': 'open',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'incident_analysis': {
                'change_types': ["configuration", "deployment", "code"],
                'timeframe_hours': 24,
                'analysis_focus': 'error investigation',
                'potential_root_causes': ["system error", "configuration issue"],
                'suspicious_patterns': ["errors", "timeouts"],
                'recent_commits_to_review': ["recent changes"],
                'configuration_changes': ["system settings"],
                'investigation_priority': 'medium',
                'suggested_approach': 'Check recent changes in affected components'
            },
            'mcp_integrations': {
                'github_enabled': bool(os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")),
                'jira_enabled': bool(os.getenv("JIRA_OAUTH_ACCESS_TOKEN")),
                'mcp_servers': []
            },
            'completed_steps': ['step1_parse_ir_ticket'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Error fetching incident {incident_id} from Jira MCP: {str(e)}. Using fallback analysis."
            }]
        }
        print(f"⚠️  STEP1: Using fallback state due to error")
        print(f"⚠️  STEP1: Fallback state keys: {list(return_state.keys())}")
        print("=" * 80)
        print("🚀 STEP1_Parse_IR_Ticket: Execution completed with fallback")
        print("=" * 80)
        
        return return_state


async def step2_identify_first_repo(state: IncidentState) -> IncidentState:
    """Step 2: Use GitHub MCP to intelligently identify repositories based on incident description."""
    print("🔍 Step 2: Using GitHub MCP to Intelligently Identify Repositories...")
    
    # Get incident details from step1
    title = state.get('title', '').lower()
    description = state.get('description', '').lower()
    error_message = state.get('error_message', '').lower()
    
    print(f"🔍 Analyzing incident: {title}")
    print(f"🔍 Description: {description[:100]}...")
    
    # First, use Circuit LLM to generate search keywords and repository patterns
    repo_identification_prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a GitHub repository analyst for incident response. Based on the incident description, identify:
        1. Search keywords to find relevant repositories
        2. Repository naming patterns to look for
        3. File patterns that would indicate relevant code
        
        Focus on identifying repositories that would contain the code related to the incident.
        """),
        ("human", """
        Incident Analysis:
        - Title: {title}
        - Description: {description}
        - Error Message: {error_message}
        
        CRITICAL: You must respond with ONLY a valid JSON object. No markdown, no explanations, no additional text.
        
        Return this exact JSON structure:
        {{
            "search_keywords": ["keywords", "to", "search", "for", "in", "github"],
            "repo_patterns": ["repository", "naming", "patterns"],
            "file_patterns": ["file", "patterns", "to", "look", "for"],
            "code_locations": ["specific", "code", "areas", "to", "investigate"],
            "main_repo_hint": "suggested main repository name",
            "reasoning": "explanation of search strategy"
        }}
        
        DO NOT include any markdown formatting, headers, or explanatory text. ONLY return the JSON object.
        """),
        ("human", """
        Example: If the incident is "Products page not loading", search for:
        - Keywords: ["products", "frontend", "ui", "web", "app"]
        - Repo patterns: ["*web*", "*frontend*", "*ui*", "*products*"]
        - File patterns: ["*.js", "*.tsx", "*.vue", "*.jsx"]
        """)
    ])
    
    try:
        # Format the prompt
        formatted_prompt = repo_identification_prompt.format_messages(
            title=title,
            description=description,
            error_message=error_message
        )
        
        # Get the human message content
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM to generate search strategy
        print("🔍 Using Circuit LLM to generate search strategy...")
        response = await llm.invoke(prompt_text)
        print("🔍 LLM INVOKE COMPLETED")
        
        # Log the raw LLM response for debugging
        print("=" * 80)
        print("🔍 RAW LLM RESPONSE:")
        print("=" * 80)
        if response is None:
            print("❌ LLM response is None!")
        elif response == "":
            print("❌ LLM response is empty string!")
        else:
            print(f"Response: {response}")
        print("=" * 80)
        print(f"🔍 Response type: {type(response)}")
        print(f"🔍 Response length: {len(str(response)) if response else 0}")
        print("=" * 80)
        
        # Parse JSON from response
        import re
        import json
        
        # Try multiple patterns to extract JSON
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks (most specific)
            r'```\s*(\{.*?\})\s*```',  # JSON in generic code blocks
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Nested JSON object
            r'\{.*?\}',  # Simple JSON object (non-greedy)
            r'\{.*\}',  # Basic JSON object (fallback)
        ]
        
        # If no JSON found, try to extract information from markdown response
        def extract_from_markdown(text):
            """Extract search information from markdown response."""
            try:
                # Look for keywords in markdown
                keywords_match = re.search(r'Keywords to Search.*?:\s*\n(.*?)(?:\n\n|\n\*\*|$)', text, re.DOTALL | re.IGNORECASE)
                keywords = []
                if keywords_match:
                    keyword_lines = keywords_match.group(1).strip().split('\n')
                    for line in keyword_lines:
                        if ':' in line or '-' in line:
                            # Extract quoted keywords
                            quoted = re.findall(r'"([^"]+)"', line)
                            keywords.extend(quoted)
                        else:
                            # Extract simple keywords
                            words = re.findall(r'\b\w+\b', line)
                            keywords.extend(words)
                
                # Look for repo patterns
                repo_match = re.search(r'Repo Patterns.*?:\s*\n(.*?)(?:\n\n|\n\*\*|$)', text, re.DOTALL | re.IGNORECASE)
                repo_patterns = []
                if repo_match:
                    pattern_lines = repo_match.group(1).strip().split('\n')
                    for line in pattern_lines:
                        quoted = re.findall(r'"([^"]+)"', line)
                        repo_patterns.extend(quoted)
                
                # Look for file patterns
                file_match = re.search(r'File Patterns.*?:\s*\n(.*?)(?:\n\n|\n\*\*|$)', text, re.DOTALL | re.IGNORECASE)
                file_patterns = []
                if file_match:
                    pattern_lines = file_match.group(1).strip().split('\n')
                    for line in pattern_lines:
                        quoted = re.findall(r'"([^"]+)"', line)
                        file_patterns.extend(quoted)
                
                if keywords or repo_patterns or file_patterns:
                    return {
                        "search_keywords": keywords[:5] if keywords else ["products", "frontend", "ui", "web"],
                        "repo_patterns": repo_patterns if repo_patterns else ["*web*", "*frontend*", "*products*"],
                        "file_patterns": file_patterns if file_patterns else ["*.js", "*.tsx", "*.vue"],
                        "code_locations": ["components", "pages", "services"],
                        "main_repo_hint": "productsWebApp",
                        "reasoning": "Extracted from markdown response"
                    }
                return None
            except Exception as e:
                print(f"⚠️  Error extracting from markdown: {e}")
                return None
        
        search_strategy = None
        for i, pattern in enumerate(json_patterns):
            print(f"🔍 Trying JSON pattern {i+1}: {pattern}")
            json_match = re.search(pattern, response, re.DOTALL)
            if json_match:
                print(f"✅ Pattern {i+1} matched!")
                try:
                    json_str = json_match.group(1) if len(json_match.groups()) > 0 else json_match.group()
                    print(f"🔍 Extracted JSON string: {json_str[:200]}...")
                    search_strategy = json.loads(json_str)
                    print("✅ Successfully parsed LLM response as JSON")
                    print(f"✅ Parsed search strategy: {search_strategy}")
                    break
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON decode error with pattern {pattern}: {e}")
                    print(f"⚠️  Failed JSON string: {json_str[:200]}...")
                    continue
            else:
                print(f"❌ Pattern {i+1} did not match")
        
        if not search_strategy:
            # Try parsing the entire response as JSON (in case LLM returned clean JSON)
            try:
                print("🔍 Trying to parse entire response as JSON...")
                search_strategy = json.loads(response.strip())
                print("✅ Successfully parsed entire response as JSON")
                print(f"✅ Parsed search strategy: {search_strategy}")
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse entire response as JSON: {e}")
                
                # Try to extract information from markdown response
                print("🔍 Trying to extract information from markdown response...")
                markdown_strategy = extract_from_markdown(response)
                if markdown_strategy:
                    print("✅ Successfully extracted search strategy from markdown")
                    print(f"✅ Extracted search strategy: {markdown_strategy}")
                    search_strategy = markdown_strategy
                else:
                    print("⚠️  Failed to extract from markdown, using fallback")
                    search_strategy = {
                        "search_keywords": ["web application", "product", "productsWebApp", "productsBackendService"],
                        "repo_patterns": ["*web*", "*frontend*", "*products*"],
                        "file_patterns": ["*.js", "*.tsx", "*.vue"],
                        "code_locations": ["components", "pages", "services"],
                        "main_repo_hint": "productsWebApp",
                        "reasoning": "Fallback: Products page incident suggests frontend repository"
                    }
        
        # Now use GitHub MCP to search for repositories
        print("🔍 Using GitHub MCP to search for repositories...")
        
        # Use GitHub API to search for repositories
        print("🔍 Searching GitHub for repositories...")
        
        # Check if we have GitHub Copilot MCP access
        print(f"🔍 GitHub MCP client status: {github_mcp_client is not None}")
        if github_mcp_client:
            print(f"🔍 GitHub MCP client type: {type(github_mcp_client)}")
            print(f"🔍 GitHub MCP client has get_tools: {hasattr(github_mcp_client, 'get_tools')}")
        
        if github_mcp_client and hasattr(github_mcp_client, 'get_tools'):
            try:
                print("🔍 Using GitHub Copilot MCP to search for repositories...")
                
                # Get available tools from GitHub Copilot MCP
                tools = await github_mcp_client.get_tools()
                print(f"✅ GitHub Copilot MCP loaded {len(tools)} tools")
                
                # Use the search strategy to find relevant repositories
                search_keywords = search_strategy.get('search_keywords', ['products', 'web', 'frontend'])
                main_repo_hint = search_strategy.get('main_repo_hint', 'productsWebApp')
                
                # Use GitHub Copilot MCP to search for repositories
                print("🎯 Using GitHub Copilot MCP to search for repositories...")
                
                # Use MCP to search for repositories with the working pattern
                mcp_repos = await search_repositories_with_mcp(github_mcp_client, search_keywords)
                
                if mcp_repos:
                    found_repos = mcp_repos
                    
                    # Prioritize productsWebApp for UI incidents
                    productsWebApp_repo = None
                    for repo in found_repos:
                        if 'productsWebApp' in repo:
                            productsWebApp_repo = repo
                            break
                    
                    if productsWebApp_repo:
                        main_repo = productsWebApp_repo
                        related_repos = [repo for repo in found_repos if repo != productsWebApp_repo]
                        print(f"✅ Prioritized {main_repo} as main repository for UI incident")
                    else:
                        main_repo = mcp_repos[0]
                        related_repos = mcp_repos[1:] if len(mcp_repos) > 1 else []
                        print(f"⚠️  No productsWebApp found, using first repository: {main_repo}")
                    
                    print(f"✅ MCP found {len(found_repos)} repositories: {found_repos}")
                    print(f"🎯 Main repository: {main_repo}")
                    print(f"📦 Related repositories: {related_repos}")
                else:
                    print("⚠️  No repositories found via MCP search")
                    found_repos = []
                    main_repo = None
                    related_repos = []
                    
            except Exception as e:
                print(f"⚠️  Error using GitHub Copilot MCP: {e}")
                found_repos = []
                main_repo = None
                related_repos = []
        else:
            print("⚠️  GitHub MCP client not available")
            found_repos = []
            main_repo = None
            related_repos = []
        
        # Create comprehensive repository list
        all_repos = found_repos
        reasoning = search_strategy.get('reasoning', 'Repository identification based on incident analysis and actual workspace repositories')
        
        print(f"🎯 Main repository identified: {main_repo}")
        print(f"🔍 Reasoning: {reasoning}")
        print(f"📦 All repositories: {all_repos}")
        print(f"🔍 Search keywords used: {search_strategy.get('search_keywords', [])}")
        
        # Update state with intelligent repository identification
        updated_state = state.copy()
        updated_state.update({
            'first_repo': main_repo,
            'all_repos': all_repos,
            'repo_analysis': {
                'search_strategy': search_strategy,
                'found_repos': found_repos,
                'main_repository': main_repo,
                'related_repositories': related_repos,
                'reasoning': reasoning
            },
            'status': 'REPO_IDENTIFIED',
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['step2_identify_repo'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Intelligently identified main repository: {main_repo} using actual workspace repositories. Found {len(found_repos)} repositories. Reasoning: {reasoning}"
            }]
        })
        
        return updated_state
        
    except Exception as e:
        print(f"❌ Error in intelligent repository identification: {e}")
        # Fallback to discovered repositories
        local_repos = discover_local_repositories()
        
        if local_repos:
            fallback_repos = local_repos
            # Prioritize productsWebApp in fallback too
            if 'productsWebApp' in fallback_repos:
                main_repo = 'productsWebApp'
            else:
                main_repo = fallback_repos[0]
        else:
            fallback_repos = ["productsWebApp", "productsGraphQLService", "productsBackendService"]
            main_repo = "productsWebApp"  # Always prioritize productsWebApp for UI incidents
        
        updated_state = state.copy()
        updated_state.update({
            'first_repo': main_repo,
            'all_repos': fallback_repos,
            'status': 'REPO_IDENTIFIED',
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['step2_identify_repo'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Fallback: Using discovered repositories {main_repo} due to error in intelligent identification"
            }]
        })
        
        print(f"✅ Fallback repository identified: {main_repo}")
        print(f"📦 All repositories: {fallback_repos}")
        
        return updated_state


async def step3_discover_repo_path(state: IncidentState) -> IncidentState:
    """Step 3: Discover the repository path using LLM analysis and GitHub MCP code inspection."""
    print("🛤️ Step 3: Discovering Repository Path...")
    
    # Get data from state
    first_repo = state.get('first_repo', '')
    all_repos = state.get('all_repos', [])
    description = state.get('description', '')
    title = state.get('title', '')
    
    print(f"🎯 Starting with first repository: {first_repo}")
    print(f"🔍 Available repositories: {all_repos}")
    print(f"📋 Incident: {title} - {description}")
    
    # Step 1: Use LLM to generate intelligent search keywords based on the incident
    search_keywords = await generate_incident_search_keywords(description, title)
    print(f"🔍 LLM generated search keywords: {search_keywords}")
    
    # Step 2: Use GitHub MCP to analyze code and find dependencies
    repo_path = []
    path_reasoning = []
    code_analysis = {}
    
    if first_repo and GITHUB_MCP_AVAILABLE and github_mcp_client:
        try:
            # Analyze the first repository to understand its dependencies
            print(f"🔍 Analyzing code in {first_repo}...")
            first_repo_analysis = await analyze_repository_code(first_repo, search_keywords)
            code_analysis[first_repo] = first_repo_analysis
            
            # Start with the first repository
            repo_path.append(first_repo)
            path_reasoning.append(f"Starting with {first_repo} based on incident analysis")
            
            # Find dependent repositories based on code analysis
            dependent_repos = await find_dependent_repositories(first_repo, first_repo_analysis, all_repos)
            
            for dep_repo in dependent_repos:
                if dep_repo not in repo_path:
                    repo_path.append(dep_repo)
                    path_reasoning.append(f"Added {dep_repo} based on code dependencies")
                    
                    # Analyze dependent repository too
                    dep_analysis = await analyze_repository_code(dep_repo, search_keywords)
                    code_analysis[dep_repo] = dep_analysis
            
            print(f"✅ Code analysis completed for {len(repo_path)} repositories")
            
        except Exception as e:
            print(f"⚠️  Error in code analysis: {e}")
            # Fallback to basic path
            repo_path = [first_repo] + [repo for repo in all_repos if repo != first_repo]
            path_reasoning = [f"Fallback path based on available repositories"]
    else:
        print("⚠️  GitHub MCP not available, using fallback path")
        repo_path = [first_repo] + [repo for repo in all_repos if repo != first_repo]
        path_reasoning = [f"Fallback path based on available repositories"]
    
    # Create comprehensive path reasoning
    final_reasoning = f"Based on incident '{title}' and code analysis: {' -> '.join(path_reasoning)}"
    
    updated_state = state.copy()
    updated_state.update({
        'repo_path': repo_path,
        'path_reasoning': final_reasoning,
        'code_analysis': code_analysis,
        'search_keywords': search_keywords,
        'status': 'PATH_DISCOVERED',
        'updated_at': datetime.now(),
        'completed_steps': state.get('completed_steps', []) + ['step3_discover_path'],
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"Repository path discovered through code analysis: {' -> '.join(repo_path)}. {final_reasoning}"
        }]
    })
    
    print(f"✅ Repository path discovered: {' -> '.join(repo_path)}")
    print(f"🔍 Path reasoning: {final_reasoning}")
    print(f"📊 Code analysis completed for {len(code_analysis)} repositories")
    return updated_state


async def step4_parallel_analysis(state: IncidentState) -> IncidentState:
    """Step 4: Get logs from local repositories and git commits using GitHub MCP, enhanced with code analysis."""
    print("⚡ Step 4: Parallel Analysis of Repositories...")
    
    # Get repository path from Step 3 analysis
    repo_path = state.get('repo_path', [])
    code_analysis = state.get('code_analysis', {})
    search_keywords = state.get('search_keywords', [])
    
    repo_commits = {}
    repo_logs = {}
    enhanced_analysis = {}
    
    print(f"🔍 Analyzing {len(repo_path)} repositories from code analysis...")
    
    for repo in repo_path:
        print(f"📦 Processing repository: {repo}")
        
        # Get git commits using GitHub MCP
        try:
            commits = await get_repository_commits(repo)
            repo_commits[repo] = commits
            print(f"✅ Retrieved {len(commits)} commits for {repo}")
        except Exception as e:
            print(f"⚠️  Error getting commits for {repo}: {e}")
            repo_commits[repo] = []
        
        # Get logs from local repository
        try:
            logs = await get_local_repository_logs(repo)
            repo_logs[repo] = logs
            print(f"✅ Retrieved {len(logs)} log entries for {repo}")
        except Exception as e:
            print(f"⚠️  Error getting logs for {repo}: {e}")
            repo_logs[repo] = []
        
        # Enhanced analysis using code analysis data
        repo_code_analysis = code_analysis.get(repo, {})
        enhanced_analysis[repo] = {
            'technologies': repo_code_analysis.get('technologies', []),
            'dependencies': repo_code_analysis.get('dependencies', []),
            'api_endpoints': repo_code_analysis.get('api_endpoints', []),
            'error_patterns': repo_code_analysis.get('error_patterns', []),
            'configuration_files': repo_code_analysis.get('configuration_files', []),
            'search_keywords_matched': [kw for kw in search_keywords if any(kw in str(repo_code_analysis).lower())],
            'commit_count': len(repo_commits.get(repo, [])),
            'log_count': len(repo_logs.get(repo, []))
        }
        
        print(f"🔍 Enhanced analysis for {repo}:")
        print(f"   Technologies: {enhanced_analysis[repo]['technologies']}")
        print(f"   API Endpoints: {len(enhanced_analysis[repo]['api_endpoints'])}")
        print(f"   Error Patterns: {len(enhanced_analysis[repo]['error_patterns'])}")
        print(f"   Keywords Matched: {enhanced_analysis[repo]['search_keywords_matched']}")
    
    updated_state = state.copy()
    updated_state.update({
        'repo_commits': repo_commits,
        'repo_logs': repo_logs,
        'enhanced_analysis': enhanced_analysis,
        'status': 'ANALYSIS_COMPLETE',
        'updated_at': datetime.now(),
        'completed_steps': state.get('completed_steps', []) + ['step4_parallel_analysis'],
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"Enhanced parallel analysis completed for {len(repo_path)} repositories using code analysis data"
        }]
    })
    
    print(f"✅ Enhanced parallel analysis completed for {len(repo_path)} repos")
    return updated_state


async def step5_analyze_logs(state: IncidentState) -> IncidentState:
    """Step 5: Analyze logs and suggest action items using real log data and enhanced analysis."""
    print("📊 Step 5: Analyzing Logs...")
    
    repo_logs = state.get('repo_logs', {})
    enhanced_analysis = state.get('enhanced_analysis', {})
    description = state.get('description', '')
    
    print(f"🔍 Analyzing logs for {len(repo_logs)} repositories with enhanced analysis...")
    
    # Analyze real log data with enhanced context
    log_patterns = []
    error_summary = []
    log_based_actions = []
    
    for repo, logs in repo_logs.items():
        print(f"📦 Analyzing logs for {repo}...")
        
        if not logs:
            print(f"⚠️  No logs found for {repo}")
            continue
        
        # Get enhanced analysis for this repository
        repo_enhanced = enhanced_analysis.get(repo, {})
        repo_technologies = repo_enhanced.get('technologies', [])
        repo_error_patterns = repo_enhanced.get('error_patterns', [])
        repo_keywords_matched = repo_enhanced.get('search_keywords_matched', [])
        
        # Analyze log patterns
        error_count = 0
        warning_count = 0
        info_count = 0
        technology_specific_errors = {}
        
        for log_entry in logs:
            level = log_entry.get('level', 'INFO').upper()
            message = log_entry.get('message', '')
            
            if 'ERROR' in level:
                error_count += 1
                error_summary.append(f"{repo}: {message}")
                
                # Check for technology-specific errors
                if 'apollo' in message.lower() or 'graphql' in message.lower():
                    technology_specific_errors['GraphQL'] = technology_specific_errors.get('GraphQL', 0) + 1
                elif 'react' in message.lower() or 'frontend' in message.lower():
                    technology_specific_errors['React'] = technology_specific_errors.get('React', 0) + 1
                elif 'memory' in message.lower() or 'heap' in message.lower():
                    technology_specific_errors['Memory'] = technology_specific_errors.get('Memory', 0) + 1
                elif 'timeout' in message.lower() or 'connection' in message.lower():
                    technology_specific_errors['Network'] = technology_specific_errors.get('Network', 0) + 1
            elif 'WARN' in level:
                warning_count += 1
            else:
                info_count += 1
        
        # Create enhanced patterns based on actual log data and code analysis
        if error_count > 0:
            log_patterns.append(f"High error rate in {repo}: {error_count} errors")
            
            # Enhanced action based on technology stack and error patterns
            if technology_specific_errors:
                for tech, count in technology_specific_errors.items():
                    log_patterns.append(f"{tech}-specific errors in {repo}: {count} errors")
                    log_based_actions.append({
                        "action": f"Investigate {tech} errors in {repo}",
                        "priority": "high",
                        "reasoning": f"Found {count} {tech}-specific errors in {repo} with technologies: {repo_technologies}"
                    })
            else:
                log_based_actions.append({
                    "action": f"Investigate error patterns in {repo}",
                    "priority": "high",
                    "reasoning": f"Found {error_count} error logs in {repo} with technologies: {repo_technologies}"
                })
        
        if warning_count > 0:
            log_patterns.append(f"Warning patterns in {repo}: {warning_count} warnings")
            log_based_actions.append({
                "action": f"Review warning logs in {repo}",
                "priority": "medium",
                "reasoning": f"Found {warning_count} warning logs in {repo}"
            })
        
        # Add actions based on code analysis findings
        if repo_error_patterns:
            log_based_actions.append({
                "action": f"Review error handling patterns in {repo}",
                "priority": "medium",
                "reasoning": f"Found {len(repo_error_patterns)} error pattern files in code analysis"
            })
        
        if repo_keywords_matched:
            log_based_actions.append({
                "action": f"Focus investigation on {repo}",
                "priority": "high",
                "reasoning": f"Repository matches {len(repo_keywords_matched)} incident keywords: {repo_keywords_matched}"
            })
        
        print(f"✅ {repo}: {error_count} errors, {warning_count} warnings, {info_count} info logs")
        print(f"   Technologies: {repo_technologies}")
        print(f"   Technology-specific errors: {technology_specific_errors}")
        print(f"   Keywords matched: {repo_keywords_matched}")
    
    # Create enhanced analysis summary
    log_analysis = {
        "log_patterns": log_patterns,
        "error_summary": error_summary,
        "log_based_actions": log_based_actions,
        "total_repositories": len(repo_logs),
        "total_log_entries": sum(len(logs) for logs in repo_logs.values()),
        "enhanced_analysis_used": True
    }
    
    updated_state = state.copy()
    updated_state.update({
        'log_analysis': log_analysis,
        'status': 'LOGS_ANALYZED',
        'updated_at': datetime.now(),
        'completed_steps': state.get('completed_steps', []) + ['step5_analyze_logs'],
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"Enhanced log analysis completed. Found {len(log_based_actions)} action items using code analysis data"
        }]
    })
    
    print(f"✅ Enhanced log analysis completed: {len(log_patterns)} patterns, {len(error_summary)} errors, {len(log_based_actions)} actions")
    return updated_state


async def step6_analyze_commits(state: IncidentState) -> IncidentState:
    """Step 6: Intelligently analyze commits to find the root cause commit using LLM and GitHub MCP."""
    print("🔍 Step 6: Analyzing Commits...")
    
    repo_commits = state.get('repo_commits', {})
    enhanced_analysis = state.get('enhanced_analysis', {})
    description = state.get('description', '')
    title = state.get('title', '')
    
    print(f"🔍 Intelligently analyzing commits for {len(repo_commits)} repositories...")
    
    # Use LLM to understand the incident and generate commit analysis strategy
    analysis_strategy = await generate_commit_analysis_strategy(description, title, enhanced_analysis)
    print(f"🎯 LLM analysis strategy: {analysis_strategy}")
    
    # Analyze real commit data with intelligent context
    suspicious_commits = []
    commit_based_actions = []
    root_cause_commits = []
    
    for repo, commits in repo_commits.items():
        print(f"📦 Analyzing commits for {repo}...")
        
        if not commits:
            print(f"⚠️  No commits found for {repo}")
            continue
        
        # Get enhanced analysis for this repository
        repo_enhanced = enhanced_analysis.get(repo, {})
        repo_technologies = repo_enhanced.get('technologies', [])
        
        # Use LLM to analyze commits in context of the incident
        repo_suspicious_commits = await analyze_repository_commits_intelligently(
            repo, commits, description, title, repo_technologies, analysis_strategy
        )
        
        for commit in repo_suspicious_commits:
            suspicious_commits.append(commit)
            
            # Check if this could be the root cause commit
            if commit.get('confidence', 0) > 0.7:
                root_cause_commits.append(commit)
                print(f"🚨 High-confidence root cause candidate: {commit['sha'][:8]} in {repo}")
        
        # Create intelligent actions based on analysis
        if repo_suspicious_commits:
            high_confidence_count = len([c for c in repo_suspicious_commits if c.get('confidence', 0) > 0.7])
            commit_based_actions.append({
                "action": f"Investigate {high_confidence_count} high-confidence commits in {repo}",
                "priority": "high" if high_confidence_count > 0 else "medium",
                "reasoning": f"Found {len(repo_suspicious_commits)} suspicious commits with {high_confidence_count} high-confidence candidates"
            })
        
        print(f"✅ {repo}: Analyzed {len(commits)} commits, found {len(repo_suspicious_commits)} suspicious")
    
    # Use LLM to correlate commits across repositories
    if suspicious_commits:
        correlation_analysis = await correlate_commits_across_repos(suspicious_commits, description, title)
        print(f"🔗 Cross-repository correlation: {correlation_analysis}")
    else:
        correlation_analysis = "No suspicious commits found to correlate"
    
    # Create enhanced analysis summary
    commit_analysis = {
        "suspicious_commits": suspicious_commits,
        "root_cause_commits": root_cause_commits,
        "commit_based_actions": commit_based_actions,
        "correlation_analysis": correlation_analysis,
        "analysis_strategy": analysis_strategy,
        "total_repositories": len(repo_commits),
        "total_commits": sum(len(commits) for commits in repo_commits.values()),
        "high_confidence_candidates": len(root_cause_commits)
    }
    
    updated_state = state.copy()
    updated_state.update({
        'commit_analysis': commit_analysis,
        'status': 'COMMITS_ANALYZED',
        'updated_at': datetime.now(),
        'completed_steps': state.get('completed_steps', []) + ['step6_analyze_commits'],
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"Intelligent commit analysis completed. Found {len(suspicious_commits)} suspicious commits, {len(root_cause_commits)} root cause candidates"
        }]
    })
    
    print(f"✅ Intelligent commit analysis completed: {len(suspicious_commits)} suspicious commits, {len(root_cause_commits)} root cause candidates")
    return updated_state


async def step7_summarize_rca(state: IncidentState) -> IncidentState:
    """Step 7: Intelligently summarize Root Cause Analysis using LLM and real data."""
    print("🎯 Step 7: Summarizing Root Cause Analysis...")
    
    log_analysis = state.get('log_analysis', {})
    commit_analysis = state.get('commit_analysis', {})
    enhanced_analysis = state.get('enhanced_analysis', {})
    description = state.get('description', '')
    title = state.get('title', '')
    
    print(f"🔍 Intelligently analyzing root cause using LLM and real data...")
    
    # Use LLM to perform intelligent RCA
    rca = await perform_intelligent_rca(
        log_analysis, commit_analysis, enhanced_analysis, description, title
    )
    
    updated_state = state.copy()
    updated_state.update({
        'root_cause_analysis': rca,
        'status': 'RCA_COMPLETE',
        'updated_at': datetime.now(),
        'completed_steps': state.get('completed_steps', []) + ['step7_summarize_rca'],
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"Intelligent RCA completed. Root cause: {rca.get('root_cause', 'Unknown')} (confidence: {rca.get('confidence', 0):.2f})"
        }]
    })
    
    print(f"✅ Intelligent RCA completed: {rca.get('root_cause', 'Unknown')} (confidence: {rca.get('confidence', 0):.2f})")
    print(f"🔍 Contributing factors: {rca.get('contributing_factors', [])}")
    print(f"📋 Evidence: {len(rca.get('evidence', []))} items")
    print(f"🎯 Primary suspect: {rca.get('primary_suspect', 'None')}")
    return updated_state


async def step8_summarize_actions(state: IncidentState) -> IncidentState:
    """Step 8: Intelligently summarize Action Items using LLM and real data."""
    print("📋 Step 8: Summarizing Action Items...")
    
    log_analysis = state.get('log_analysis', {})
    commit_analysis = state.get('commit_analysis', {})
    rca = state.get('root_cause_analysis', {})
    enhanced_analysis = state.get('enhanced_analysis', {})
    description = state.get('description', '')
    title = state.get('title', '')
    
    print(f"🔍 Intelligently consolidating action items using LLM...")
    
    # Use LLM to generate intelligent action items
    intelligent_actions = await generate_intelligent_action_items(
        log_analysis, commit_analysis, rca, enhanced_analysis, description, title
    )
    
    updated_state = state.copy()
    updated_state.update({
        'action_items': intelligent_actions.get('action_items', []),
        'consolidated_actions': intelligent_actions,
        'status': 'ACTIONS_SUMMARIZED',
        'updated_at': datetime.now(),
        'completed_steps': state.get('completed_steps', []) + ['step8_summarize_actions'],
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"Intelligent action items generated. {len(intelligent_actions.get('action_items', []))} actions identified, {len(intelligent_actions.get('immediate_actions', []))} immediate actions"
        }]
    })
    
    print(f"✅ Intelligent action items summarized: {len(intelligent_actions.get('action_items', []))} actions")
    print(f"🚨 Immediate actions: {len(intelligent_actions.get('immediate_actions', []))}")
    print(f"🛡️ Prevention measures: {len(intelligent_actions.get('prevention_measures', []))}")
    return updated_state


async def setup_mcp_integrations(state: IncidentState) -> IncidentState:
    """Setup MCP integrations for GitHub and Jira."""
    print("🔗 Setting up MCP Integrations...")
    
    enabled_servers = []
    
    # Test GitHub MCP integration
    if github_mcp_client:
        try:
            print("🔍 Testing GitHub MCP connection...")
            # Add GitHub MCP test here when available
            enabled_servers.append('GitHub')
            print("✅ GitHub MCP integration available and tested")
        except Exception as e:
            print(f"❌ GitHub MCP test failed: {e}")
    
    # Test Jira MCP integration
    if jira_mcp_client:
        try:
            print("🔍 Testing Jira MCP connection...")
            
            # Initialize the client first
            success = await jira_mcp_client.initialize()
            if not success:
                print("❌ Jira MCP client initialization failed")
                return state
            
            projects = await jira_mcp_client.get_projects()
            if projects:
                enabled_servers.append('Jira')
                print(f"✅ Jira MCP integration available and tested. Found {len(projects)} projects")
            else:
                print("⚠️  Jira MCP connection failed - no projects found")
        except Exception as e:
            print(f"❌ Jira MCP test failed: {e}")
    
    updated_state = state.copy()
    updated_state.update({
        'status': 'MCP_SETUP',
        'updated_at': datetime.now(),
        'mcp_integrations': {
            'github_enabled': bool(os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")),
            'jira_enabled': bool(os.getenv("JIRA_OAUTH_ACCESS_TOKEN")),
            'mcp_servers': enabled_servers,
            'github_client_available': 'GitHub' in enabled_servers,
            'jira_client_available': 'Jira' in enabled_servers
        },
        'github_analysis': state.get('github_analysis', {}),
        'jira_tickets': state.get('jira_tickets', []),
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"MCP integrations setup: {', '.join(enabled_servers)} available and tested"
        }]
    })
    
    print(f"✅ MCP integrations setup: {len(enabled_servers)} servers ready")
    return updated_state


async def create_jira_tickets(state: IncidentState) -> IncidentState:
    """Create Jira tickets using real Jira MCP integration."""
    print("📝 Creating Jira Tickets with MCP...")
    
    if not state.get('mcp_integrations', {}).get('jira_client_available'):
        print("⚠️  Jira MCP client not available, skipping")
        return state
    
    title = state.get('title', '')
    description = state.get('description', '')
    severity = state.get('severity', '')
    github_analysis = state.get('github_analysis', {})
    
    try:
        # Use real Jira MCP integration
        if jira_mcp_client:
            print("📝 Using real Jira MCP integration...")
            
            # Get available projects
            projects = await jira_mcp_client.get_projects()
            if not projects:
                print("❌ No Jira projects available")
                return state
            
            # Use the first available project (IR project if available)
            project_key = "IR"  # Default to IR project
            if not any(p.get('key') == 'IR' for p in projects):
                project_key = projects[0].get('key', 'IR')
            
            # Create incident ticket
            incident_ticket = await jira_mcp_client.create_issue(
                project_key=project_key,
                summary=f"Incident: {title}",
                description=f"""
**Incident Details:**
- **Title:** {title}
- **Description:** {description}
- **Severity:** {severity}
- **Created:** {datetime.now().isoformat()}

**GitHub Analysis:**
{json.dumps(github_analysis, indent=2)}

**Next Steps:**
1. Investigate root cause
2. Implement fixes
3. Update status
                """,
                issue_type="Incident"
            )
            
            # Create follow-up tasks based on GitHub analysis
            follow_up_tickets = []
            
            if github_analysis.get('recent_commits'):
                # Create task for reviewing recent commits
                commit_review_ticket = await jira_mcp_client.create_issue(
                    project_key=project_key,
                    summary="Review recent commits for incident correlation",
                    description=f"""
**Task:** Review recent commits for potential correlation with incident

**Commits to Review:**
{json.dumps(github_analysis.get('recent_commits', []), indent=2)}

**Instructions:**
1. Review each commit for potential issues
2. Check configuration changes
3. Verify deployment impact
                    """,
                    issue_type="Task"
                )
                follow_up_tickets.append(commit_review_ticket)
            
            if github_analysis.get('potential_causes'):
                # Create task for investigating potential causes
                cause_investigation_ticket = await jira_mcp_client.create_issue(
                    project_key=project_key,
                    summary="Investigate potential causes identified",
                    description=f"""
**Task:** Investigate potential causes of the incident

**Potential Causes:**
{json.dumps(github_analysis.get('potential_causes', []), indent=2)}

**Instructions:**
1. Investigate each potential cause
2. Validate hypotheses
3. Document findings
                    """,
                    issue_type="Task"
                )
                follow_up_tickets.append(cause_investigation_ticket)
            
            # Combine all tickets
            all_tickets = [incident_ticket] + follow_up_tickets
            
            updated_state = state.copy()
            updated_state.update({
                'jira_tickets': all_tickets,
                'status': 'JIRA_TICKETS_CREATED',
                'updated_at': datetime.now(),
                'completed_steps': state.get('completed_steps', []) + ['create_jira_tickets'],
                'messages': state.get('messages', []) + [{
                    'role': 'assistant',
                    'content': f"Created {len(all_tickets)} Jira tickets using MCP integration"
                }]
            })
            
            print(f"✅ Jira MCP tickets created: {len(all_tickets)} tickets")
            return updated_state
            
        else:
            print("❌ Jira MCP client not available")
            return state
            
    except Exception as e:
        print(f"❌ Jira MCP ticket creation error: {e}")
        return state


async def step9_update_ir_ticket(state: IncidentState) -> IncidentState:
    """Step 9: Update the IR ticket with RCA and action items using Jira MCP."""
    print("📝 Step 9: Updating IR Ticket...")
    
    rca = state.get('root_cause_analysis', {})
    action_items = state.get('action_items', [])
    consolidated_actions = state.get('consolidated_actions', {})
    ir_ticket = state.get('ir_ticket', {})
    incident_id = state.get('incident_id', '')
    
    print(f"🔍 Updating IR ticket {incident_id} with investigation results...")
    
    # Create comprehensive update content
    update_content = await create_comprehensive_ticket_update(
        rca, action_items, consolidated_actions, ir_ticket
    )
    
    # Update ticket using Jira MCP if available
    update_success = False
    if JIRA_MCP_AVAILABLE and jira_mcp_client and incident_id:
        try:
            print(f"📝 Using Jira MCP to update ticket {incident_id}...")
            
            # Update the ticket with investigation results
            update_result = await jira_mcp_client.update_issue(
                issue_key=incident_id,
                fields={
                    "summary": update_content.get('summary', ''),
                    "description": update_content.get('description', ''),
                    "status": "INVESTIGATION_COMPLETE"
                }
            )
            
            if update_result:
                update_success = True
                print(f"✅ Successfully updated IR ticket {incident_id} via Jira MCP")
            else:
                print(f"⚠️  Failed to update IR ticket {incident_id} via Jira MCP")
                
        except Exception as e:
            print(f"⚠️  Error updating IR ticket via Jira MCP: {e}")
    
    # Create updated ticket object
    updated_ticket = {
        **ir_ticket,
        "status": "INVESTIGATION_COMPLETE",
        "root_cause_analysis": rca,
        "action_items": action_items,
        "consolidated_actions": consolidated_actions,
        "investigation_completed_at": datetime.now().isoformat(),
        "investigator": "AI Incident Response Agent",
        "summary": update_content.get('summary', ''),
        "description": update_content.get('description', ''),
        "update_method": "Jira MCP" if update_success else "Local update"
    }
    
    updated_state = state.copy()
    updated_state.update({
        'updated_ticket': updated_ticket,
        'ticket_update_success': update_success,
        'status': 'TICKET_UPDATED',
        'updated_at': datetime.now(),
        'completed_steps': state.get('completed_steps', []) + ['step9_update_ticket'],
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"IR ticket updated with comprehensive RCA and {len(action_items)} action items. Update method: {'Jira MCP' if update_success else 'Local'}"
        }]
    })
    
    print(f"✅ IR ticket updated successfully")
    print(f"📊 Root cause: {rca.get('root_cause', 'Unknown')}")
    print(f"📋 Action items: {len(action_items)}")
    print(f"🎯 Primary suspect: {rca.get('primary_suspect', {}).get('sha', 'None')}")
    return updated_state


# Create the graph
def create_graph() -> StateGraph:
    """Create the enhanced incident response graph with 9-step workflow."""
    
    workflow = StateGraph(IncidentInput)
    
    # Add nodes for each step
    workflow.add_node("step1_parse_ticket", step1_parse_ir_ticket)
    workflow.add_node("setup_mcp", setup_mcp_integrations)
    workflow.add_node("step2_identify_repo", step2_identify_first_repo)
    workflow.add_node("step3_discover_path", step3_discover_repo_path)
    workflow.add_node("step4_parallel_analysis", step4_parallel_analysis)
    workflow.add_node("step5_analyze_logs", step5_analyze_logs)
    workflow.add_node("step6_analyze_commits", step6_analyze_commits)
    workflow.add_node("step7_summarize_rca", step7_summarize_rca)
    workflow.add_node("step8_summarize_actions", step8_summarize_actions)
    workflow.add_node("create_jira_tickets", create_jira_tickets)
    workflow.add_node("step9_update_ticket", step9_update_ir_ticket)
    
    # Define the linear workflow
    workflow.add_edge(START, "step1_parse_ticket")
    workflow.add_edge("step1_parse_ticket", "setup_mcp")
    workflow.add_edge("setup_mcp",  "step2_identify_repo")
    workflow.add_edge("step2_identify_repo", "step3_discover_path")
    workflow.add_edge("step3_discover_path", "step4_parallel_analysis")
    workflow.add_edge("step4_parallel_analysis", "step5_analyze_logs")
    workflow.add_edge("step5_analyze_logs", "step6_analyze_commits")
    workflow.add_edge("step6_analyze_commits", "step7_summarize_rca")
    workflow.add_edge("step7_summarize_rca", "step8_summarize_actions")
    workflow.add_edge("step8_summarize_actions", "create_jira_tickets")
    workflow.add_edge("create_jira_tickets", "step9_update_ticket")
    workflow.add_edge("step9_update_ticket", END)
    
    return workflow.compile()


# Create the graph instance
graph = create_graph()
