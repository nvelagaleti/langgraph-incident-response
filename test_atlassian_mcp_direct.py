#!/usr/bin/env python3
"""
Direct test of Atlassian MCP server using HTTP requests.
"""

import asyncio
import os
import json
import httpx
from dotenv import load_dotenv
from token_manager import TokenManager


async def test_atlassian_mcp_server():
    """Test Atlassian MCP server directly."""
    print("🔗 Testing Atlassian MCP Server Directly")
    print("=" * 50)
    
    # Load environment and get token
    load_dotenv()
    token_manager = TokenManager()
    access_token = await token_manager.ensure_valid_token()
    
    if not access_token:
        print("❌ No access token available")
        return
    
    print(f"✅ Using access token: {access_token[:20]}...")
    
    # Atlassian MCP server URL
    mcp_url = "https://mcp.atlassian.com/v1/sse"
    
    # Test different endpoints
    endpoints = [
        "/health",
        "/tools",
        "/resources",
        "/"
    ]
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for endpoint in endpoints:
            url = f"{mcp_url}{endpoint}"
            print(f"\n🔍 Testing endpoint: {url}")
            
            try:
                response = await client.get(url, headers=headers)
                print(f"📊 Status: {response.status_code}")
                print(f"📋 Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ Response: {json.dumps(data, indent=2)[:500]}...")
                    except:
                        print(f"✅ Response: {response.text[:500]}...")
                else:
                    print(f"❌ Error response: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Test SSE (Server-Sent Events) connection
    print(f"\n🔍 Testing SSE connection to: {mcp_url}")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("GET", mcp_url, headers=headers) as response:
                print(f"📊 SSE Status: {response.status_code}")
                print(f"📋 SSE Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    print("✅ SSE connection established")
                    # Read first few events
                    count = 0
                    async for line in response.aiter_lines():
                        if count >= 5:  # Only read first 5 lines
                            break
                        print(f"📨 Event {count + 1}: {line}")
                        count += 1
                else:
                    print(f"❌ SSE connection failed: {response.text}")
                    
    except Exception as e:
        print(f"❌ SSE Error: {e}")


async def test_mcp_protocol():
    """Test MCP protocol messages."""
    print(f"\n🔧 Testing MCP Protocol Messages")
    print("=" * 50)
    
    # Load environment and get token
    load_dotenv()
    token_manager = TokenManager()
    access_token = await token_manager.ensure_valid_token()
    
    if not access_token:
        print("❌ No access token available")
        return
    
    # Atlassian MCP server URL
    mcp_url = "https://mcp.atlassian.com/v1/sse"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    # MCP protocol messages
    mcp_messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "LangGraph-Incident-Response",
                    "version": "1.0.0"
                }
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, message in enumerate(mcp_messages):
            print(f"\n📤 Sending MCP message {i + 1}: {message['method']}")
            
            try:
                response = await client.post(
                    mcp_url,
                    headers=headers,
                    json=message
                )
                print(f"📊 Status: {response.status_code}")
                print(f"📋 Response: {response.text[:500]}...")
                
            except Exception as e:
                print(f"❌ Error: {e}")


async def main():
    """Main function."""
    await test_atlassian_mcp_server()
    await test_mcp_protocol()


if __name__ == "__main__":
    asyncio.run(main())
