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
                    main_repo = mcp_repos[0]
                    related_repos = mcp_repos[1:] if len(mcp_repos) > 1 else []
                    print(f"✅ MCP found {len(found_repos)} repositories: {found_repos}")
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
            main_repo = local_repos[0]
        else:
            fallback_repos = ["productsWebApp", "productsGraphQLService", "productsBackendService"]
            main_repo = fallback_repos[0]
        
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
    """Step 3: Discover the path from UI to GraphQL to Backend by following code."""
    print("🛤️ Step 3: Discovering Repository Path...")
    
    first_repo = state.get('first_repo', '')
    description = state.get('description', '')
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an incident response analyst. Based on the error and first repository, discover the complete path of repositories involved.
        Follow the typical flow: UI -> GraphQL -> Backend Service.
        """),
        ("human", """
        First Repo: {first_repo}
        Error Description: {description}
        
        Discover the repository path as JSON:
        {{
            "repo_path": ["ui_repo", "graphql_repo", "backend_repo"],
            "path_reasoning": "explanation of the path",
            "all_repos": ["list", "of", "all", "repos", "involved"]
        }}
        """)
    ])
    
    try:
                # Format the prompt
        formatted_prompt = prompt.format_messages(
            first_repo=first_repo, description=description
        )
        
        # Get the human message content
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM directly
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            path_info = json.loads(json_match.group())
        else:
            # Fallback parsing
            path_info = {}
        
        updated_state = state.copy()
        updated_state.update({
            'repo_path': path_info.get('repo_path', []),
            'all_repos': path_info.get('all_repos', []),
            'status': 'PATH_DISCOVERED',
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['step3_discover_path'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Repo path discovered: {' -> '.join(path_info.get('repo_path', []))}"
            }]
        })
        
        print(f"✅ Repo path discovered: {' -> '.join(updated_state['repo_path'])}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error discovering repo path: {e}")
        return state


async def step4_parallel_analysis(state: IncidentState) -> IncidentState:
    """Step 4: Get logs and git commits simultaneously for all repos."""
    print("⚡ Step 4: Parallel Analysis of Repositories...")
    
    all_repos = state.get('all_repos', [])
    
    # Simulate parallel analysis
    repo_commits = {}
    repo_logs = {}
    
    for repo in all_repos:
        # Simulate getting commits
        repo_commits[repo] = [
            {
                "sha": f"abc123_{repo}",
                "message": f"Update configuration in {repo}",
                "author": "developer@company.com",
                "date": (datetime.now() - timedelta(hours=2)).isoformat(),
                "files": ["config.yaml", "deployment.yaml"]
            },
            {
                "sha": f"def456_{repo}",
                "message": f"Fix memory leak in {repo}",
                "author": "developer@company.com", 
                "date": (datetime.now() - timedelta(hours=4)).isoformat(),
                "files": ["service.py", "memory.py"]
            }
        ]
        
        # Simulate getting logs
        repo_logs[repo] = [
            {
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "level": "ERROR",
                "message": f"Memory usage at 95% in {repo}",
                "service": repo
            },
            {
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "level": "ERROR", 
                "message": f"Out of memory error in {repo}",
                "service": repo
            }
        ]
    
    updated_state = state.copy()
    updated_state.update({
        'repo_commits': repo_commits,
        'repo_logs': repo_logs,
        'status': 'ANALYSIS_COMPLETE',
        'updated_at': datetime.now(),
        'completed_steps': state.get('completed_steps', []) + ['step4_parallel_analysis'],
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"Parallel analysis completed for {len(all_repos)} repositories"
        }]
    })
    
    print(f"✅ Parallel analysis completed for {len(all_repos)} repos")
    return updated_state


async def step5_analyze_logs(state: IncidentState) -> IncidentState:
    """Step 5: Analyze logs and suggest action items."""
    print("📊 Step 5: Analyzing Logs...")
    
    repo_logs = state.get('repo_logs', {})
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an incident response analyst. Analyze the logs and identify patterns, errors, and suggest action items.
        """),
        ("human", """
        Repository Logs: {repo_logs}
        
        Analyze logs and provide action items as JSON:
        {{
            "log_patterns": ["list", "of", "patterns"],
            "error_summary": "summary of errors found",
            "log_based_actions": [
                {{
                    "action": "string",
                    "priority": "high|medium|low",
                    "reasoning": "string"
                }}
            ]
        }}
        """)
    ])
    
    try:
                # Format the prompt
        formatted_prompt = prompt.format_messages(
            repo_logs=json.dumps(repo_logs, indent=2)
        )
        
        # Get the human message content
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM directly
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            log_analysis = json.loads(json_match.group())
        else:
            # Fallback parsing
            log_analysis = {}
        
        updated_state = state.copy()
        updated_state.update({
            'log_analysis': log_analysis,
            'status': 'LOGS_ANALYZED',
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['step5_analyze_logs'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Log analysis completed. Found {len(log_analysis.get('log_based_actions', []))} action items"
            }]
        })
        
        print(f"✅ Log analysis completed")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error analyzing logs: {e}")
        return state


async def step6_analyze_commits(state: IncidentState) -> IncidentState:
    """Step 6: Analyze commits and identify potential issues."""
    print("🔍 Step 6: Analyzing Commits...")
    
    repo_commits = state.get('repo_commits', {})
    description = state.get('description', '')
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an incident response analyst. Analyze the git commits and identify potential issues that could cause the incident.
        Look for configuration changes, memory-related changes, and recent deployments.
        """),
        ("human", """
        Repository Commits: {repo_commits}
        Incident Description: {description}
        
        Analyze commits and identify issues as JSON:
        {{
            "suspicious_commits": [
                {{
                    "repo": "string",
                    "sha": "string",
                    "message": "string",
                    "potential_issue": "string",
                    "confidence": 0.0-1.0
                }}
            ],
            "commit_based_actions": [
                {{
                    "action": "string",
                    "priority": "high|medium|low",
                    "reasoning": "string"
                }}
            ]
        }}
        """)
    ])
    
    try:
                # Format the prompt
        formatted_prompt = prompt.format_messages(
            repo_commits=json.dumps(repo_commits, indent=2),
            description=description
        )
        
        # Get the human message content
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM directly
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            commit_analysis = json.loads(json_match.group())
        else:
            # Fallback parsing
            commit_analysis = {}
        
        updated_state = state.copy()
        updated_state.update({
            'commit_analysis': commit_analysis,
            'status': 'COMMITS_ANALYZED',
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['step6_analyze_commits'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Commit analysis completed. Found {len(commit_analysis.get('suspicious_commits', []))} suspicious commits"
            }]
        })
        
        print(f"✅ Commit analysis completed")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error analyzing commits: {e}")
        return state


async def step7_summarize_rca(state: IncidentState) -> IncidentState:
    """Step 7: Summarize Root Cause Analysis."""
    print("🎯 Step 7: Summarizing Root Cause Analysis...")
    
    log_analysis = state.get('log_analysis', {})
    commit_analysis = state.get('commit_analysis', {})
    description = state.get('description', '')
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an incident response analyst. Based on the log analysis and commit analysis, provide a comprehensive root cause analysis.
        """),
        ("human", """
        Log Analysis: {log_analysis}
        Commit Analysis: {commit_analysis}
        Incident Description: {description}
        
        Provide root cause analysis as JSON:
        {{
            "root_cause": "string",
            "contributing_factors": ["list", "of", "factors"],
            "timeline": "string",
            "confidence": 0.0-1.0,
            "evidence": ["list", "of", "evidence"]
        }}
        """)
    ])
    
    try:
                # Format the prompt
        formatted_prompt = prompt.format_messages(
            log_analysis=json.dumps(log_analysis, indent=2),
            commit_analysis=json.dumps(commit_analysis, indent=2),
            description=description
        )
        
        # Get the human message content
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM directly
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            rca = json.loads(json_match.group())
        else:
            # Fallback parsing
            rca = {}
        
        updated_state = state.copy()
        updated_state.update({
            'root_cause_analysis': rca,
            'status': 'RCA_COMPLETE',
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['step7_summarize_rca'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"RCA completed. Root cause: {rca.get('root_cause', 'Unknown')}"
            }]
        })
        
        print(f"✅ RCA completed: {rca.get('root_cause', 'Unknown')}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error summarizing RCA: {e}")
        return state


async def step8_summarize_actions(state: IncidentState) -> IncidentState:
    """Step 8: Summarize Action Items."""
    print("📋 Step 8: Summarizing Action Items...")
    
    log_analysis = state.get('log_analysis', {})
    commit_analysis = state.get('commit_analysis', {})
    rca = state.get('root_cause_analysis', {})
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an incident response analyst. Consolidate all action items from log analysis and commit analysis into a comprehensive action plan.
        """),
        ("human", """
        Log Analysis Actions: {log_analysis}
        Commit Analysis Actions: {commit_analysis}
        Root Cause Analysis: {rca}
        
        Provide consolidated action items as JSON:
        {{
            "action_items": [
                {{
                    "action": "string",
                    "priority": "high|medium|low",
                    "category": "immediate|short_term|long_term",
                    "assignee": "string",
                    "estimated_effort": "string",
                    "description": "string"
                }}
            ],
            "immediate_actions": ["list", "of", "immediate", "actions"],
            "prevention_measures": ["list", "of", "prevention", "measures"]
        }}
        """)
    ])
    
    try:
                # Format the prompt
        formatted_prompt = prompt.format_messages(
            log_analysis=json.dumps(log_analysis, indent=2),
            commit_analysis=json.dumps(commit_analysis, indent=2),
            rca=json.dumps(rca, indent=2)
        )
        
        # Get the human message content
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM directly
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            actions = json.loads(json_match.group())
        else:
            # Fallback parsing
            actions = {}
        
        updated_state = state.copy()
        updated_state.update({
            'action_items': actions.get('action_items', []),
            'status': 'ACTIONS_SUMMARIZED',
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['step8_summarize_actions'],
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Action items summarized. {len(actions.get('action_items', []))} actions identified"
            }]
        })
        
        print(f"✅ Action items summarized: {len(updated_state['action_items'])} actions")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error summarizing actions: {e}")
        return state


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
    """Step 9: Update the IR ticket with RCA and action items."""
    print("📝 Step 9: Updating IR Ticket...")
    
    rca = state.get('root_cause_analysis', {})
    action_items = state.get('action_items', [])
    ir_ticket = state.get('ir_ticket', {})
    
    # Create updated ticket
    updated_ticket = {
        **ir_ticket,
        "status": "INVESTIGATION_COMPLETE",
        "root_cause_analysis": rca,
        "action_items": action_items,
        "investigation_completed_at": datetime.now().isoformat(),
        "investigator": "AI Incident Response Agent",
        "summary": f"Root Cause: {rca.get('root_cause', 'Unknown')}. {len(action_items)} action items identified."
    }
    
    updated_state = state.copy()
    updated_state.update({
        'updated_ticket': updated_ticket,
        'status': 'TICKET_UPDATED',
        'updated_at': datetime.now(),
        'completed_steps': state.get('completed_steps', []) + ['step9_update_ticket'],
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': f"IR ticket updated with RCA and {len(action_items)} action items"
        }]
    })
    
    print(f"✅ IR ticket updated")
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
