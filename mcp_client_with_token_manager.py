#!/usr/bin/env python3
"""
Enhanced MCP Client with Token Manager Integration
Automatically handles token renewal and provides seamless MCP integration
"""

import os
import asyncio
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from token_manager import TokenManager

class MCPClientWithTokenManager:
    """Enhanced MCP client with automatic token management."""
    
    def __init__(self):
        load_dotenv()
        self.token_manager = TokenManager()
        self.mcp_client = None
        self.servers_config = {}
        
    async def initialize(self):
        """Initialize the MCP client with valid tokens."""
        print("🚀 Initializing Enhanced MCP Client")
        print("=" * 50)
        
        # Ensure we have a valid token
        token = await self.token_manager.ensure_valid_token()
        if not token:
            print("❌ Failed to obtain valid token")
            return False
        
        # Configure MCP servers
        self.servers_config = {
            "jira": {
                "transport": "streamable_http",
                "url": "https://api.atlassian.com/mcp",
                "headers": {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "LangGraph-Incident-Response/1.0"
                }
            }
        }
        
        try:
            from langchain_mcp_adapters.client import MultiServerMCPClient
            
            self.mcp_client = MultiServerMCPClient(self.servers_config)
            tools = await self.mcp_client.get_tools()
            
            print(f"✅ MCP client initialized successfully")
            print(f"📊 Tools loaded: {len(tools)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize MCP client: {e}")
            return False
    
    async def get_tools(self) -> List[Any]:
        """Get MCP tools with automatic token renewal."""
        if not self.mcp_client:
            success = await self.initialize()
            if not success:
                return []
        
        try:
            # Check if token is still valid
            if not self.token_manager.is_token_valid():
                print("🔄 Token expired, renewing...")
                await self.token_manager.ensure_valid_token()
                
                # Reinitialize with new token
                await self.initialize()
            
            return await self.mcp_client.get_tools()
            
        except Exception as e:
            print(f"❌ Error getting tools: {e}")
            return []
    
    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Invoke a specific tool with automatic token renewal."""
        if not self.mcp_client:
            success = await self.initialize()
            if not success:
                return None
        
        try:
            tools = await self.get_tools()
            
            # Find the tool
            target_tool = None
            for tool in tools:
                if hasattr(tool, 'name') and tool.name == tool_name:
                    target_tool = tool
                    break
            
            if not target_tool:
                print(f"❌ Tool '{tool_name}' not found")
                return None
            
            # Invoke the tool
            result = await target_tool.ainvoke(arguments)
            return result
            
        except Exception as e:
            print(f"❌ Error invoking tool '{tool_name}': {e}")
            return None
    
    async def test_jira_operations(self):
        """Test Jira operations with automatic token management."""
        print("🧪 Testing Jira Operations with Token Manager")
        print("=" * 60)
        
        tools = await self.get_tools()
        if not tools:
            print("❌ No tools available")
            return False
        
        # Create tool map
        tool_map = {}
        for tool in tools:
            if hasattr(tool, 'name'):
                tool_map[tool.name] = tool
        
        print(f"📊 Available tools: {len(tool_map)}")
        
        # Test 1: Get projects
        print(f"\n🔍 Test 1: Getting Projects")
        if 'get_projects' in tool_map:
            try:
                result = await self.invoke_tool('get_projects', {})
                print(f"✅ get_projects: Success")
                print(f"📄 Result: {str(result)[:200]}...")
            except Exception as e:
                print(f"❌ get_projects: {str(e)[:50]}...")
        else:
            print("❌ get_projects tool not found")
        
        # Test 2: Search issues
        print(f"\n🔍 Test 2: Searching Issues")
        if 'search_issues' in tool_map:
            try:
                result = await self.invoke_tool('search_issues', {
                    "jql": "ORDER BY created DESC",
                    "max_results": 5
                })
                print(f"✅ search_issues: Success")
                print(f"📄 Result: {str(result)[:200]}...")
            except Exception as e:
                print(f"❌ search_issues: {str(e)[:50]}...")
        else:
            print("❌ search_issues tool not found")
        
        return True
    
    async def close(self):
        """Close the MCP client."""
        if self.mcp_client:
            try:
                await self.mcp_client.aclose()
                print("✅ MCP client closed")
            except Exception as e:
                print(f"⚠️  Error closing MCP client: {e}")

class TokenAwareMCPWrapper:
    """Wrapper for existing MCP scripts to add token management."""
    
    def __init__(self, original_script_path: str):
        self.original_script_path = original_script_path
        self.token_manager = TokenManager()
        self.mcp_client = None
    
    async def run_with_token_management(self):
        """Run the original script with automatic token management."""
        print(f"🔄 Running {self.original_script_path} with token management")
        print("=" * 60)
        
        # Ensure valid token before running
        token = await self.token_manager.ensure_valid_token()
        if not token:
            print("❌ Failed to obtain valid token")
            return False
        
        # Set environment variable for the script
        os.environ["JIRA_OAUTH_ACCESS_TOKEN"] = token
        
        try:
            # Import and run the original script
            import importlib.util
            spec = importlib.util.spec_from_file_location("original_script", self.original_script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # If the module has a main function, run it
            if hasattr(module, 'main'):
                if asyncio.iscoroutinefunction(module.main):
                    await module.main()
                else:
                    module.main()
            
            return True
            
        except Exception as e:
            print(f"❌ Error running original script: {e}")
            return False

async def main():
    """Main function to demonstrate token-managed MCP client."""
    print("🚀 Enhanced MCP Client with Token Manager")
    print("=" * 60)
    
    # Initialize enhanced client
    client = MCPClientWithTokenManager()
    
    # Test initialization
    success = await client.initialize()
    if not success:
        print("❌ Failed to initialize client")
        return
    
    # Test Jira operations
    await client.test_jira_operations()
    
    # Show token status
    print(f"\n🔍 Token Status:")
    status = client.token_manager.get_token_status()
    print(f"   Valid: {status['expiry_info']['valid']}")
    print(f"   Expires: {status['expiry_info']['expires_at']}")
    print(f"   Time until expiry: {status['expiry_info']['time_until_expiry']}")
    
    # Close client
    await client.close()
    
    print(f"\n🎉 Enhanced MCP client test completed!")

if __name__ == "__main__":
    asyncio.run(main())
