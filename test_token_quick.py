#!/usr/bin/env python3
"""
Quick Token Test
Test if a GitHub token works with public GitHub API
"""

import os
import requests
from dotenv import load_dotenv

def test_token():
    """Test if the current token works."""
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        print("❌ No token found in .env file")
        return False
    
    print(f"🔑 Testing token: {token[:10]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    try:
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Token works!")
            print(f"   User: {user_data.get('login')}")
            print(f"   Name: {user_data.get('name')}")
            return True
        else:
            print(f"❌ Token failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_token()
