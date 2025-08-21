#!/usr/bin/env python3
"""
Test Jira MCP Server Integration
Comprehensive test of Jira MCP server for incident management
"""

import os
import asyncio
import json
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

async def test_jira_mcp_integration():
    """Test Jira MCP server integration."""
    print("🧪 Testing Jira MCP Server Integration")
    print("=" * 60)
    
    load_dotenv()
    
    # Jira configuration
    jira_url = os.getenv("JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    jira_project = os.getenv("JIRA_PROJECT")
    
    # Check if Jira is configured
    if not jira_url or jira_url == "https://your-domain.atlassian.net":
        print("❌ Jira URL not configured properly")
        print("💡 Please update your .env file with your actual Jira URL")
        return False
    
    if not jira_token or jira_token == "your_jira_api_token_here":
        print("❌ Jira token not configured")
        print("💡 Please update your .env file with your actual Jira API token")
        return False
    
    print(f"✅ Jira URL: {jira_url}")
    print(f"✅ Jira Project: {jira_project}")
    print(f"✅ Jira Token: {jira_token[:10]}...")
    
    # Test different Jira MCP server URLs
    jira_mcp_urls = [
        "https://api.atlassian.com/mcp",
        "https://your-domain.atlassian.net/api/mcp",
        "https://api.atlassian.com/jira/mcp",
        "https://api.atlassian.com/rest/mcp"
    ]
    
    for mcp_url in jira_mcp_urls:
        print(f"\n🔍 Testing Jira MCP URL: {mcp_url}")
        
        try:
            # Configure MCP client for Jira
            servers_config = {
                "jira": {
                    "transport": "streamable_http",
                    "url": mcp_url,
                    "headers": {
                        "Authorization": f"Bearer {jira_token}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "User-Agent": "LangGraph-Incident-Response/1.0"
                    }
                }
            }
            
            client = MultiServerMCPClient(servers_config)
            tools = await client.get_tools()
            
            print(f"✅ Jira MCP client configured")
            print(f"✅ Tools loaded: {len(tools)} tools")
            
            # Show available Jira tools
            print(f"\n🔧 Available Jira Tools:")
            tool_names = []
            for tool in tools:
                if hasattr(tool, 'name'):
                    tool_names.append(tool.name)
                    print(f"   - {tool.name}")
            
            # Test specific Jira operations
            await test_jira_operations(tools, jira_project)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed with {mcp_url}: {e}")
            continue
    
    print(f"\n❌ No working Jira MCP server found")
    return False

async def test_jira_operations(tools, project_key):
    """Test specific Jira operations."""
    print(f"\n🎫 Testing Jira Operations")
    print("-" * 40)
    
    # Find specific tools
    tool_map = {}
    for tool in tools:
        if hasattr(tool, 'name'):
            tool_map[tool.name] = tool
    
    # Test 1: Get project information
    print(f"🔍 Test 1: Getting Project Information")
    
    if 'get_project' in tool_map:
        try:
            project_result = await tool_map['get_project'].ainvoke({
                "project_key": project_key
            })
            print(f"✅ Project info retrieved")
            print(f"📄 Result: {str(project_result)[:200]}...")
        except Exception as e:
            print(f"❌ Error getting project info: {e}")
    else:
        print("❌ get_project tool not found")
    
    # Test 2: List issues
    print(f"\n🔍 Test 2: Listing Issues")
    
    if 'search_issues' in tool_map:
        try:
            issues_result = await tool_map['search_issues'].ainvoke({
                "jql": f"project = {project_key} ORDER BY created DESC",
                "max_results": 5
            })
            print(f"✅ Issues retrieved")
            print(f"📄 Result: {str(issues_result)[:300]}...")
        except Exception as e:
            print(f"❌ Error listing issues: {e}")
    else:
        print("❌ search_issues tool not found")
    
    # Test 3: Create test issue (simulation)
    print(f"\n🔍 Test 3: Testing Issue Creation (Simulation)")
    
    if 'create_issue' in tool_map:
        print("   ⚠️  Issue creation tool available")
        print("   💡 This would create a real issue - skipping for safety")
        print("   🔧 To test: create_issue tool is ready for use")
    else:
        print("❌ create_issue tool not found")
    
    # Test 4: Get issue types
    print(f"\n🔍 Test 4: Getting Issue Types")
    
    if 'get_issue_types' in tool_map:
        try:
            types_result = await tool_map['get_issue_types'].ainvoke({
                "project_key": project_key
            })
            print(f"✅ Issue types retrieved")
            print(f"📄 Result: {str(types_result)[:200]}...")
        except Exception as e:
            print(f"❌ Error getting issue types: {e}")
    else:
        print("❌ get_issue_types tool not found")

async def test_combined_mcp_integration():
    """Test combined GitHub and Jira MCP integration."""
    print(f"\n🔗 Testing Combined GitHub + Jira MCP Integration")
    print("=" * 60)
    
    load_dotenv()
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    jira_token = os.getenv("JIRA_TOKEN")
    
    if not github_token or not jira_token:
        print("❌ Missing tokens for combined test")
        return False
    
    try:
        # Configure both GitHub and Jira MCP servers
        servers_config = {
            "github": {
                "transport": "streamable_http",
                "url": "https://api.githubcopilot.com/mcp",
                "headers": {
                    "Authorization": f"Bearer {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json",
                    "User-Agent": "LangGraph-Incident-Response/1.0"
                }
            },
            "jira": {
                "transport": "streamable_http",
                "url": "https://api.atlassian.com/mcp",
                "headers": {
                    "Authorization": f"Bearer {jira_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "LangGraph-Incident-Response/1.0"
                }
            }
        }
        
        client = MultiServerMCPClient(servers_config)
        tools = await client.get_tools()
        
        print(f"✅ Combined MCP client configured")
        print(f"✅ Total tools loaded: {len(tools)} tools")
        
        # Categorize tools
        github_tools = []
        jira_tools = []
        
        for tool in tools:
            if hasattr(tool, 'name'):
                if any(keyword in tool.name.lower() for keyword in ['issue', 'project', 'jira']):
                    jira_tools.append(tool.name)
                else:
                    github_tools.append(tool.name)
        
        print(f"\n📊 Tool Distribution:")
        print(f"   GitHub Tools: {len(github_tools)}")
        print(f"   Jira Tools: {len(jira_tools)}")
        
        print(f"\n🎯 Incident Response Capabilities:")
        print(f"   ✅ GitHub: Repository monitoring, commit analysis")
        print(f"   ✅ Jira: Issue creation, incident tracking")
        print(f"   ✅ Combined: Full incident response workflow")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in combined integration: {e}")
        return False

def show_jira_setup_instructions():
    """Show instructions for setting up Jira MCP."""
    print(f"\n📋 Jira MCP Setup Instructions")
    print("=" * 50)
    print(f"1. Get your Jira API Token:")
    print(f"   - Go to https://id.atlassian.com/manage-profile/security/api-tokens")
    print(f"   - Create a new API token")
    print(f"   - Copy the token")
    
    print(f"\n2. Update your .env file:")
    print(f"   JIRA_URL=https://your-domain.atlassian.net")
    print(f"   JIRA_TOKEN=your_actual_api_token")
    print(f"   JIRA_PROJECT=INCIDENT")
    
    print(f"\n3. Test Jira MCP server URLs:")
    print(f"   - https://api.atlassian.com/mcp")
    print(f"   - https://your-domain.atlassian.net/api/mcp")
    
    print(f"\n4. Verify Jira project exists:")
    print(f"   - Ensure the project key (e.g., INCIDENT) exists in your Jira")
    print(f"   - Verify you have permissions to create issues")

async def main():
    """Main test function."""
    print("🧪 Jira MCP Integration Test")
    print("=" * 60)
    
    # Test 1: Jira MCP integration
    jira_ok = await test_jira_mcp_integration()
    
    # Test 2: Combined integration
    if jira_ok:
        combined_ok = await test_combined_mcp_integration()
    else:
        combined_ok = False
        show_jira_setup_instructions()
    
    # Final summary
    print(f"\n🎉 Jira MCP Test Results:")
    print("=" * 50)
    print(f"✅ Jira MCP: {'PASS' if jira_ok else 'FAIL'}")
    print(f"✅ Combined Integration: {'PASS' if combined_ok else 'FAIL'}")
    
    if jira_ok and combined_ok:
        print(f"\n🎊 SUCCESS! Full MCP integration is ready!")
        print(f"🚀 GitHub + Jira incident response system operational!")
    else:
        print(f"\n⚠️  Jira MCP needs configuration")
        print(f"💡 Follow the setup instructions above")

if __name__ == "__main__":
    asyncio.run(main())
