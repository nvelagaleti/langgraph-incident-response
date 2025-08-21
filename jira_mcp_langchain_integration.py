#!/usr/bin/env python3
"""
Jira MCP Server Integration with LangChain
Integrates Jira MCP Server with LangChain MCP adapter and token management
"""

import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from token_manager import TokenManager

# Import LangChain components
try:
    from langchain_mcp import MCPToolkit
    from langgraph.agent import Agent
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    from langchain_core.messages import HumanMessage, AIMessage
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  LangChain components not available: {e}")
    print("💡 Install with: pip install langchain-mcp langgraph langchain-openai")
    LANGCHAIN_AVAILABLE = False

class JiraMCPLangChainIntegration:
    """Integrates Jira MCP Server with LangChain and token management."""
    
    def __init__(self):
        load_dotenv()
        self.token_manager = TokenManager()
        self.mcp_toolkit = None
        self.agent = None
        self.llm = None
        
    async def initialize(self):
        """Initialize the MCP toolkit with token management."""
        print("🚀 Initializing Jira MCP LangChain Integration")
        print("=" * 60)
        
        if not LANGCHAIN_AVAILABLE:
            print("❌ LangChain components not available")
            return False
        
        # Ensure we have a valid token
        token = await self.token_manager.ensure_valid_token()
        if not token:
            print("❌ Failed to obtain valid token")
            return False
        
        print(f"✅ Token validated successfully")
        
        try:
            # Initialize MCP toolkit with OAuth token
            print("🔗 Initializing MCP Toolkit...")
            self.mcp_toolkit = MCPToolkit.from_mcp(
                url="https://mcp.atlassian.com/v1/sse",
                auth_mode="oauth",
                oauth_token=token
            )
            
            print(f"✅ MCP Toolkit initialized successfully")
            print(f"📊 Available tools: {len(self.mcp_toolkit.tools)}")
            
            # Initialize LLM
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    temperature=0,
                    api_key=openai_api_key
                )
                print("✅ LLM initialized with OpenAI")
            else:
                print("⚠️  No OpenAI API key found, using default LLM")
                self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            # Initialize agent
            self.agent = Agent(tools=self.mcp_toolkit.tools, llm=self.llm)
            print("✅ Agent initialized successfully")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing MCP toolkit: {e}")
            return False
    
    def list_available_tools(self):
        """List all available MCP tools."""
        if not self.mcp_toolkit:
            print("❌ MCP toolkit not initialized")
            return
        
        print(f"\n🔧 Available Jira MCP Tools ({len(self.mcp_toolkit.tools)} total)")
        print("=" * 60)
        
        for i, tool in enumerate(self.mcp_toolkit.tools, 1):
            print(f"\n{i}. Tool: {tool.name}")
            print(f"   📝 Description: {tool.description}")
            print(f"   🔧 Type: {type(tool).__name__}")
            
            # Show input schema if available
            if hasattr(tool, 'args_schema'):
                print(f"   📋 Input Schema: {tool.args_schema}")
    
    async def get_projects_using_mcp(self) -> List[Dict[str, Any]]:
        """Get Jira projects using MCP tools."""
        print(f"\n🔍 Getting Jira Projects via MCP")
        print("-" * 40)
        
        if not self.mcp_toolkit:
            print("❌ MCP toolkit not initialized")
            return []
        
        try:
            # Find the get_projects tool
            get_projects_tool = None
            for tool in self.mcp_toolkit.tools:
                if tool.name == 'get_projects':
                    get_projects_tool = tool
                    break
            
            if not get_projects_tool:
                print("❌ get_projects tool not found")
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
    
    async def create_incident_issue(self, project_key: str, summary: str, description: str) -> Dict[str, Any]:
        """Create an incident issue using MCP tools."""
        print(f"\n🎫 Creating Incident Issue")
        print("-" * 40)
        
        if not self.mcp_toolkit:
            print("❌ MCP toolkit not initialized")
            return {}
        
        try:
            # Find the create_issue tool
            create_issue_tool = None
            for tool in self.mcp_toolkit.tools:
                if tool.name == 'create_issue':
                    create_issue_tool = tool
                    break
            
            if not create_issue_tool:
                print("❌ create_issue tool not found")
                return {}
            
            print("✅ Found create_issue tool")
            
            # Prepare issue data
            issue_data = {
                "project_key": project_key,
                "summary": summary,
                "description": description,
                "issue_type": "Incident"
            }
            
            print(f"🔄 Creating issue in project: {project_key}")
            print(f"📝 Summary: {summary}")
            
            # Invoke the tool
            result = await create_issue_tool.ainvoke(issue_data)
            
            if isinstance(result, str):
                try:
                    issue_data = json.loads(result)
                except json.JSONDecodeError:
                    print("❌ Failed to parse issue data")
                    return {}
            else:
                issue_data = result
            
            print(f"✅ Issue created successfully")
            return issue_data
            
        except Exception as e:
            print(f"❌ Error creating issue: {e}")
            return {}
    
    async def search_issues(self, jql: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search issues using MCP tools."""
        print(f"\n🔍 Searching Issues via MCP")
        print("-" * 40)
        
        if not self.mcp_toolkit:
            print("❌ MCP toolkit not initialized")
            return []
        
        try:
            # Find the search_issues tool
            search_issues_tool = None
            for tool in self.mcp_toolkit.tools:
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
    
    async def run_agent_query(self, query: str) -> str:
        """Run a query through the LangChain agent."""
        print(f"\n🤖 Running Agent Query")
        print("-" * 40)
        
        if not self.agent:
            print("❌ Agent not initialized")
            return "Agent not available"
        
        try:
            print(f"📝 Query: {query}")
            
            # Run the agent
            result = await self.agent.ainvoke({
                "messages": [HumanMessage(content=query)]
            })
            
            response = result.get("messages", [])[-1].content if result.get("messages") else "No response"
            print(f"✅ Agent response received")
            
            return response
            
        except Exception as e:
            print(f"❌ Error running agent query: {e}")
            return f"Error: {str(e)}"
    
    def create_state_graph(self):
        """Create a LangGraph state graph for incident response."""
        print(f"\n🔄 Creating Incident Response State Graph")
        print("-" * 40)
        
        if not self.mcp_toolkit:
            print("❌ MCP toolkit not initialized")
            return None
        
        try:
            # Create state graph
            workflow = StateGraph(AgentState)
            
            # Add nodes
            workflow.add_node("agent", self.agent)
            workflow.add_node("tools", ToolNode(self.mcp_toolkit.tools))
            
            # Add edges
            workflow.add_edge("agent", "tools")
            workflow.add_edge("tools", "agent")
            workflow.add_edge("agent", END)
            
            # Set entry point
            workflow.set_entry_point("agent")
            
            # Compile the graph
            app = workflow.compile()
            
            print("✅ State graph created successfully")
            return app
            
        except Exception as e:
            print(f"❌ Error creating state graph: {e}")
            return None

# State definition for LangGraph
class AgentState:
    messages: List[Any]
    tools: List[Any]

async def main():
    """Main function to demonstrate Jira MCP LangChain integration."""
    print("🚀 Jira MCP LangChain Integration Demo")
    print("=" * 60)
    
    # Initialize integration
    integration = JiraMCPLangChainIntegration()
    
    # Initialize connection
    success = await integration.initialize()
    if not success:
        print("❌ Failed to initialize integration")
        return
    
    try:
        # List available tools
        integration.list_available_tools()
        
        # Get projects using MCP
        projects = await integration.get_projects_using_mcp()
        
        if projects:
            print(f"\n📋 Retrieved {len(projects)} projects via MCP")
            
            # Display first few projects
            for i, project in enumerate(projects[:3], 1):
                print(f"{i}. {project.get('key', 'N/A')} - {project.get('name', 'N/A')}")
            
            # Test agent query
            print(f"\n🤖 Testing Agent Query")
            query = "What are the available Jira projects?"
            response = await integration.run_agent_query(query)
            print(f"📝 Response: {response[:200]}...")
            
            # Test issue search
            print(f"\n🔍 Testing Issue Search")
            issues = await integration.search_issues("ORDER BY created DESC", max_results=5)
            print(f"📊 Found {len(issues)} recent issues")
            
            # Create state graph
            graph = integration.create_state_graph()
            if graph:
                print("✅ Incident response workflow ready!")
            
        else:
            print("❌ No projects found via MCP")
            
    except Exception as e:
        print(f"❌ Error during integration demo: {e}")
    
    print(f"\n✅ Integration demo completed")

if __name__ == "__main__":
    asyncio.run(main())
