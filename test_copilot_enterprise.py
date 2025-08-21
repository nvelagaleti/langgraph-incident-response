#!/usr/bin/env python3
"""
Test GitHub Copilot MCP Server with Enterprise Account
Tests if we can access the MCP server with enterprise Copilot integration
"""

import os
import asyncio
import requests
from dotenv import load_dotenv

def test_copilot_mcp_direct():
    """Test GitHub Copilot MCP server directly."""
    print("🔍 Testing GitHub Copilot MCP Server Direct Access")
    print("=" * 60)
    
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    mcp_url = "https://api.githubcopilot.com/mcp"
    
    if not token:
        print("❌ No token found in .env file")
        return False
    
    print(f"🔑 Token: {token[:10]}...")
    print(f"🌐 MCP URL: {mcp_url}")
    
    # Test different authentication methods
    auth_methods = [
        {"Authorization": f"Bearer {token}"},
        {"Authorization": f"token {token}"},
        {"X-GitHub-Token": token},
        {"GitHub-Token": token}
    ]
    
    for i, auth_header in enumerate(auth_methods, 1):
        print(f"\n🔧 Testing Auth Method {i}: {list(auth_header.keys())[0]}")
        
        headers = {
            **auth_header,
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "LangGraph-Incident-Response/1.0"
        }
        
        try:
            # Test health endpoint
            health_url = f"{mcp_url}/health"
            print(f"   Testing: {health_url}")
            
            response = requests.get(health_url, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS with {list(auth_header.keys())[0]}")
                print(f"   Response: {response.text[:200]}...")
                return True
            elif response.status_code == 401:
                print(f"   ❌ Unauthorized")
            elif response.status_code == 404:
                print(f"   ⚠️  Not found (endpoint doesn't exist)")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

async def test_copilot_mcp_langchain():
    """Test GitHub Copilot MCP server with LangChain."""
    print("\n🔌 Testing GitHub Copilot MCP Server with LangChain")
    print("=" * 60)
    
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    mcp_url = "https://api.githubcopilot.com/mcp"
    
    if not token:
        print("❌ No token found in .env file")
        return False
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        # Test different server configurations
        configs = [
            {
                "github": {
                    "transport": "streamable_http",
                    "url": mcp_url,
                    "headers": {
                        "Authorization": f"Bearer {token}",
                        "Accept": "application/vnd.github.v3+json",
                        "Content-Type": "application/json",
                        "User-Agent": "LangGraph-Incident-Response/1.0"
                    }
                }
            },
            {
                "github": {
                    "transport": "streamable_http",
                    "url": mcp_url,
                    "headers": {
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github.v3+json",
                        "Content-Type": "application/json",
                        "User-Agent": "LangGraph-Incident-Response/1.0"
                    }
                }
            }
        ]
        
        for i, config in enumerate(configs, 1):
            print(f"\n🔧 Testing LangChain Config {i}")
            print(f"   Auth: {config['github']['headers']['Authorization'][:20]}...")
            
            try:
                client = MultiServerMCPClient(config)
                print("   ✅ MultiServerMCPClient created")
                
                tools = await client.get_tools()
                print(f"   ✅ Tools loaded: {len(tools)} tools")
                
                # Show available tools
                print("   📋 Available Tools:")
                for tool_name, tool in list(tools.items())[:5]:
                    print(f"      - {tool_name}: {tool.name}")
                
                return True
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                continue
        
        return False
        
    except Exception as e:
        print(f"❌ Error in LangChain test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enterprise_copilot_features():
    """Test if we can access enterprise Copilot features."""
    print("\n🏢 Testing Enterprise Copilot Features")
    print("=" * 60)
    
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        print("❌ No token found in .env file")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    # Test enterprise-specific endpoints
    endpoints = [
        "https://api.githubcopilot.com/user",
        "https://api.githubcopilot.com/enterprise",
        "https://api.githubcopilot.com/copilot",
        "https://api.githubcopilot.com/features"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"🔍 Testing: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Accessible")
                print(f"   Response: {response.text[:200]}...")
            elif response.status_code == 401:
                print(f"   ❌ Unauthorized")
            elif response.status_code == 404:
                print(f"   ⚠️  Not found")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main test function."""
    print("🧪 GitHub Copilot Enterprise MCP Test")
    print("=" * 60)
    
    # Test 1: Direct MCP access
    direct_ok = test_copilot_mcp_direct()
    
    # Test 2: LangChain MCP access
    try:
        langchain_ok = asyncio.run(test_copilot_mcp_langchain())
    except:
        print("⚠️  Skipping LangChain test (async not available)")
        langchain_ok = False
    
    # Test 3: Enterprise Copilot features
    test_enterprise_copilot_features()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 50)
    print(f"✅ Direct MCP Access: {'PASS' if direct_ok else 'FAIL'}")
    print(f"✅ LangChain MCP: {'PASS' if langchain_ok else 'FAIL'}")
    
    if direct_ok or langchain_ok:
        print("\n🎉 GitHub Copilot MCP server is accessible!")
        print("   You can use it with your enterprise Copilot integration.")
    else:
        print("\n❌ GitHub Copilot MCP server is not accessible.")
        print("   You may need to:")
        print("   1. Check your enterprise Copilot permissions")
        print("   2. Use a different authentication method")
        print("   3. Contact your enterprise admin for MCP access")

if __name__ == "__main__":
    main()
