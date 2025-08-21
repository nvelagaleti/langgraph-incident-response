#!/usr/bin/env python3
"""
Standalone Jira MCP Integration Test
Test Jira MCP integration outside of LangGraph agent
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

async def test_jira_mcp_standalone():
    """Test Jira MCP integration standalone."""
    print("🧪 Standalone Jira MCP Integration Test")
    print("=" * 60)
    
    load_dotenv()
    
    # Get Jira configuration
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    print(f"✅ Jira URL: {jira_url}")
    print(f"✅ Jira Token: {jira_token[:20] if jira_token else 'Missing'}...")
    print(f"✅ Jira Email: {jira_email or 'Missing'}")
    
    if not jira_url or not jira_token:
        print("❌ Jira configuration missing")
        return False
    
    # Test different MCP server URLs
    mcp_urls = [
        {
            "name": "Atlassian MCP (SSE)",
            "url": "https://mcp.atlassian.com/v1/sse",
            "headers": {
                "Authorization": f"Bearer {jira_token}",
                "Accept": "text/event-stream",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Atlassian MCP (Standard)",
            "url": "https://mcp.atlassian.com/v1",
            "headers": {
                "Authorization": f"Bearer {jira_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Custom Jira MCP",
            "url": f"{jira_url}/rest/mcp",
            "headers": {
                "Authorization": f"Bearer {jira_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        }
    ]
    
    for mcp_config in mcp_urls:
        print(f"\n🔍 Testing: {mcp_config['name']}")
        print(f"   URL: {mcp_config['url']}")
        
        try:
            # Configure MCP client
            servers_config = {
                "jira": {
                    "transport": "streamable_http",
                    "url": mcp_config["url"],
                    "headers": mcp_config["headers"]
                }
            }
            
            client = MultiServerMCPClient(servers_config)
            tools = await client.get_tools()
            
            print(f"   ✅ SUCCESS: {len(tools)} tools loaded")
            
            # Show available tools
            print(f"   🔧 Available Tools:")
            for i, tool in enumerate(tools[:10]):  # Show first 10 tools
                if hasattr(tool, 'name'):
                    print(f"      {i+1}. {tool.name}")
            
            if len(tools) > 10:
                print(f"      ... and {len(tools) - 10} more tools")
            
            # Test a simple operation
            await test_jira_operations(client, tools)
            
            # Close client
            await client.aclose()
            
            print(f"   🎉 {mcp_config['name']} is working!")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)[:100]}...")
            continue
    
    print(f"\n❌ No Jira MCP server worked")
    return False

async def test_jira_operations(client, tools):
    """Test basic Jira operations."""
    print(f"   🔍 Testing Jira Operations:")
    
    # Find tools by name patterns
    tool_map = {}
    for tool in tools:
        if hasattr(tool, 'name'):
            tool_map[tool.name] = tool
    
    # Test 1: Get projects
    if 'get_projects' in tool_map:
        try:
            result = await tool_map['get_projects'].ainvoke({})
            print(f"      ✅ get_projects: Success")
            print(f"         Result: {str(result)[:100]}...")
        except Exception as e:
            print(f"      ❌ get_projects: {str(e)[:50]}...")
    
    # Test 2: Search issues
    if 'search_issues' in tool_map:
        try:
            result = await tool_map['search_issues'].ainvoke({
                "jql": "ORDER BY created DESC",
                "max_results": 5
            })
            print(f"      ✅ search_issues: Success")
            print(f"         Result: {str(result)[:100]}...")
        except Exception as e:
            print(f"      ❌ search_issues: {str(e)[:50]}...")
    
    # Test 3: Get issue types
    if 'get_issue_types' in tool_map:
        try:
            result = await tool_map['get_issue_types'].ainvoke({})
            print(f"      ✅ get_issue_types: Success")
            print(f"         Result: {str(result)[:100]}...")
        except Exception as e:
            print(f"      ❌ get_issue_types: {str(e)[:50]}...")

async def test_direct_jira_api():
    """Test direct Jira API as fallback."""
    print(f"\n🔍 Testing Direct Jira API (Fallback)")
    print("-" * 40)
    
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_email = os.getenv("JIRA_EMAIL")
    
    if not jira_url or not jira_token:
        print("❌ Jira configuration missing for direct API test")
        return False
    
    import requests
    import base64
    
    # Test different authentication methods
    auth_methods = [
        ("Bearer Token", {"Authorization": f"Bearer {jira_token}"}),
        ("Basic Auth", {"Authorization": f"Basic {base64.b64encode(f'{jira_email}:{jira_token}'.encode()).decode()}"} if jira_email else None),
        ("Token Only", {"Authorization": f"token {jira_token}"}),
    ]
    
    headers_base = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    for method_name, auth_header in auth_methods:
        if auth_header is None:
            continue
            
        print(f"🔍 Testing: {method_name}")
        try:
            headers = {**headers_base, **auth_header}
            user_url = f"{jira_url}/rest/api/3/myself"
            response = requests.get(user_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"   ✅ SUCCESS with {method_name}")
                print(f"   📄 User: {user_data.get('displayName', 'Unknown')}")
                print(f"   📄 Email: {user_data.get('emailAddress', 'Unknown')}")
                
                # Test getting projects
                projects_url = f"{jira_url}/rest/api/3/project"
                projects_response = requests.get(projects_url, headers=headers, timeout=10)
                
                if projects_response.status_code == 200:
                    projects = projects_response.json()
                    project_keys = [proj.get('key', '') for proj in projects if proj.get('key')]
                    print(f"   📄 Projects: {len(projects)} found")
                    print(f"   📋 Project Keys: {', '.join(project_keys[:5])}")
                
                return True
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"   📄 Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

async def main():
    """Main function."""
    print("🧪 Standalone Jira MCP Test")
    print("=" * 60)
    
    # Test 1: Jira MCP integration
    mcp_success = await test_jira_mcp_standalone()
    
    # Test 2: Direct Jira API
    direct_success = await test_direct_jira_api()
    
    # Final summary
    print(f"\n🎉 Standalone Jira Integration Test Results:")
    print("=" * 50)
    print(f"✅ Jira MCP Integration: {'PASS' if mcp_success else 'FAIL'}")
    print(f"✅ Direct Jira API: {'PASS' if direct_success else 'FAIL'}")
    
    if mcp_success:
        print(f"\n🎊 SUCCESS! Jira MCP integration is working!")
        print(f"🚀 Ready to integrate with LangGraph agent!")
    elif direct_success:
        print(f"\n🎊 SUCCESS! Direct Jira API is working!")
        print(f"🚀 Can use hybrid approach (GitHub MCP + Direct Jira API)!")
    else:
        print(f"\n⚠️  Both MCP and direct API failed")
        print(f"💡 Check JIRA_TOKEN_GUIDE.md for setup help")

if __name__ == "__main__":
    asyncio.run(main())
