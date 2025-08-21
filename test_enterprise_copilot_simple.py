#!/usr/bin/env python3
"""
Simple Enterprise Copilot MCP Test
Quick test for GitHub Copilot MCP server with enterprise account
"""

import os
import requests
from dotenv import load_dotenv

def main():
    load_dotenv()
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        print("❌ No token found")
        return
    
    print(f"🔑 Testing with token: {token[:10]}...")
    
    # Test GitHub Copilot MCP server
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    try:
        response = requests.get("https://api.githubcopilot.com/mcp/health", headers=headers, timeout=10)
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✅ GitHub Copilot MCP server is accessible!")
        else:
            print("❌ GitHub Copilot MCP server is not accessible")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
