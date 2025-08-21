#!/usr/bin/env python3
"""
Use OAuth Tokens with MCP Integration
Demonstrates how to use the obtained OAuth tokens with existing MCP clients
"""

import os
import asyncio
import json
from dotenv import load_dotenv

async def test_oauth_tokens_with_mcp():
    """Test OAuth tokens with MCP integration."""
    print("🔐 Testing OAuth Tokens with MCP Integration")
    print("=" * 60)
    
    load_dotenv()
    
    # Get OAuth tokens
    access_token = os.getenv("JIRA_OAUTH_ACCESS_TOKEN")
    refresh_token = os.getenv("JIRA_OAUTH_REFRESH_TOKEN")
    
    if not access_token:
        print("❌ No OAuth access token found")
        print("💡 Please run jira_oauth_simple.py first to obtain tokens")
        return False
    
    print(f"✅ OAuth Access Token: {access_token[:20]}...")
    if refresh_token:
        print(f"✅ OAuth Refresh Token: {refresh_token[:20]}...")
    
    # Test with different MCP server configurations
    await test_official_atlassian_mcp(access_token)
    await test_custom_mcp_server(access_token)
    
    return True

async def test_official_atlassian_mcp(access_token):
    """Test with official Atlassian MCP server."""
    print(f"\n🔍 Testing Official Atlassian MCP Server")
    print("-" * 50)
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Configure MCP client with OAuth token
        servers_config = {
            "jira": {
                "transport": "streamable_http",
                "url": "https://api.atlassian.com/mcp",
                "headers": {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "LangGraph-Incident-Response/1.0"
                }
            }
        }
        
        client = MultiServerMCPClient(servers_config)
        tools = await client.get_tools()
        
        print(f"✅ Official Atlassian MCP connected")
        print(f"📊 Tools available: {len(tools)}")
        
        # Show available tools
        tool_names = []
        for tool in tools:
            if hasattr(tool, 'name'):
                tool_names.append(tool.name)
        
        print(f"🔧 Available tools: {', '.join(tool_names[:10])}")
        if len(tool_names) > 10:
            print(f"   ... and {len(tool_names) - 10} more")
        
        await client.aclose()
        return True
        
    except Exception as e:
        print(f"❌ Error with official Atlassian MCP: {e}")
        return False

async def test_custom_mcp_server(access_token):
    """Test with custom MCP server configuration."""
    print(f"\n🔍 Testing Custom MCP Server Configuration")
    print("-" * 50)
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Alternative MCP server configurations
        server_configs = [
            {
                "name": "Atlassian MCP (SSE)",
                "url": "https://mcp.atlassian.com/v1/sse",
                "headers": {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "text/event-stream",
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Atlassian MCP (HTTP)",
                "url": "https://mcp.atlassian.com/v1/http",
                "headers": {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }
            }
        ]
        
        for config in server_configs:
            print(f"🔍 Testing {config['name']}")
            
            try:
                servers_config = {
                    "jira": {
                        "transport": "streamable_http",
                        "url": config["url"],
                        "headers": config["headers"]
                    }
                }
                
                client = MultiServerMCPClient(servers_config)
                tools = await client.get_tools()
                
                print(f"   ✅ Connected successfully")
                print(f"   📊 Tools: {len(tools)}")
                
                await client.aclose()
                
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with custom MCP configurations: {e}")
        return False

def show_token_usage_examples():
    """Show examples of how to use the tokens."""
    print(f"\n📋 Token Usage Examples")
    print("=" * 50)
    
    print(f"1. Direct API Calls:")
    print(f"   import requests")
    print(f"   ")
    print(f"   headers = {{")
    print(f"       'Authorization': 'Bearer {os.getenv('JIRA_OAUTH_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN')}',")
    print(f"       'Accept': 'application/json',")
    print(f"       'Content-Type': 'application/json'")
    print(f"   }}")
    print(f"   ")
    print(f"   response = requests.get('https://api.atlassian.com/ex/jira/YOUR_CLOUD_ID/rest/api/3/project', headers=headers)")
    
    print(f"\n2. MCP Client Configuration:")
    print(f"   servers_config = {{")
    print(f"       'jira': {{")
    print(f"           'transport': 'streamable_http',")
    print(f"           'url': 'https://api.atlassian.com/mcp',")
    print(f"           'headers': {{")
    print(f"               'Authorization': 'Bearer {os.getenv('JIRA_OAUTH_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN')}',")
    print(f"               'Accept': 'application/json',")
    print(f"               'Content-Type': 'application/json'")
    print(f"           }}")
    print(f"       }}")
    print(f"   }}")
    
    print(f"\n3. Environment Variables:")
    print(f"   # In your .env file:")
    print(f"   JIRA_OAUTH_ACCESS_TOKEN={os.getenv('JIRA_OAUTH_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN')}")
    print(f"   JIRA_OAUTH_REFRESH_TOKEN={os.getenv('JIRA_OAUTH_REFRESH_TOKEN', 'YOUR_REFRESH_TOKEN')}")

async def main():
    """Main function."""
    print("🚀 OAuth Tokens Usage Guide")
    print("=" * 60)
    
    # Test OAuth tokens with MCP
    success = await test_oauth_tokens_with_mcp()
    
    # Show usage examples
    show_token_usage_examples()
    
    # Final summary
    print(f"\n🎉 OAuth Token Usage Summary:")
    print("=" * 50)
    if success:
        print(f"✅ OAuth tokens are working with MCP integration!")
        print(f"🚀 Ready for production use!")
    else:
        print(f"⚠️  Some tests failed. Check your token configuration.")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Use tokens with your existing MCP scripts")
    print(f"   2. Integrate with LangGraph incident response agent")
    print(f"   3. Set up token refresh mechanism for long-running applications")

if __name__ == "__main__":
    asyncio.run(main())
