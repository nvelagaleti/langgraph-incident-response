#!/usr/bin/env python3
"""
Simple Jira MCP Integration
Matches the exact pattern from the user's example with token management
"""

import os
import asyncio
from dotenv import load_dotenv
from token_manager import TokenManager

# Import LangChain components
try:
    from langchain_mcp import MCPToolkit
    from langgraph.agent import Agent
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  LangChain components not available: {e}")
    print("💡 Install with: pip install langchain-mcp langgraph")
    LANGCHAIN_AVAILABLE = False

class SimpleJiraMCPIntegration:
    """Simple Jira MCP integration matching the user's example."""
    
    def __init__(self):
        load_dotenv()
        self.token_manager = TokenManager()
        self.jira_toolkit = None
        self.agent = None
        
    async def initialize(self):
        """Initialize the integration with token management."""
        print("🚀 Initializing Simple Jira MCP Integration")
        print("=" * 50)
        
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
            # Initialize MCP toolkit exactly as in the user's example
            print("🔗 Initializing MCP Toolkit...")
            self.jira_toolkit = MCPToolkit.from_mcp(
                url="https://mcp.atlassian.com/v1/sse",
                auth_mode="oauth",
                oauth_token=token
            )
            
            print(f"✅ MCP Toolkit initialized successfully")
            print(f"📊 Available tools: {len(self.jira_toolkit.tools)}")
            
            # Initialize agent exactly as in the user's example
            self.agent = Agent(tools=self.jira_toolkit.tools)
            print("✅ Agent initialized successfully")
            
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
    
    async def test_agent(self, query: str = "What are the available Jira projects?"):
        """Test the agent with a simple query."""
        print(f"\n🤖 Testing Agent")
        print("-" * 30)
        
        if not self.agent:
            print("❌ Agent not initialized")
            return
        
        try:
            print(f"📝 Query: {query}")
            
            # Test the agent
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": query}]
            })
            
            print(f"✅ Agent response received")
            print(f"📄 Response: {result}")
            
        except Exception as e:
            print(f"❌ Error testing agent: {e}")

async def main():
    """Main function demonstrating the simple integration."""
    print("🚀 Simple Jira MCP Integration Demo")
    print("=" * 60)
    
    # Initialize integration
    integration = SimpleJiraMCPIntegration()
    
    # Initialize connection
    success = await integration.initialize()
    if not success:
        print("❌ Failed to initialize integration")
        return
    
    try:
        # List available tools
        integration.list_tools()
        
        # Test agent
        await integration.test_agent()
        
        print(f"\n🎉 Simple integration demo completed!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")

if __name__ == "__main__":
    asyncio.run(main())
