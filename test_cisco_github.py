#!/usr/bin/env python3
"""
Cisco GitHub Enterprise Test Script
Tests connection to Cisco's internal GitHub Enterprise instance.
"""

import os
import requests
from dotenv import load_dotenv

def test_cisco_github_token():
    """Test Cisco GitHub Enterprise Personal Access Token."""
    print("🔑 Cisco GitHub Enterprise Token Test")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get token and host from environment
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    github_host = os.getenv("GITHUB_HOST", "https://wwwin-github.cisco.com")
    
    if not token:
        print("❌ No GitHub token found in .env file")
        print("   Set GITHUB_PERSONAL_ACCESS_TOKEN in your .env file")
        return False
    
    print(f"✅ Token found: {token[:10]}...")
    print(f"✅ GitHub Host: {github_host}")
    
    # Test Cisco GitHub Enterprise API
    print(f"\n🔗 Testing Cisco GitHub Enterprise API...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    try:
        # Test user endpoint
        user_url = f"{github_host}/api/v3/user"
        print(f"📡 Testing: {user_url}")
        
        response = requests.get(user_url, headers=headers, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Token is valid!")
            print(f"   User: {user_data.get('login', 'Unknown')}")
            print(f"   Name: {user_data.get('name', 'Unknown')}")
            print(f"   Email: {user_data.get('email', 'Unknown')}")
            print(f"   Company: {user_data.get('company', 'Unknown')}")
            
            # Test rate limit
            rate_limit_url = f"{github_host}/api/v3/rate_limit"
            rate_limit_response = requests.get(rate_limit_url, headers=headers, timeout=10)
            if rate_limit_response.status_code == 200:
                rate_data = rate_limit_response.json()
                core = rate_data.get('resources', {}).get('core', {})
                print(f"   Rate limit: {core.get('remaining', 'Unknown')}/{core.get('limit', 'Unknown')} requests remaining")
            
            return True
            
        elif response.status_code == 401:
            print("❌ Token is invalid or expired")
            print("   Response:", response.json().get('message', 'Unknown error'))
            return False
            
        elif response.status_code == 403:
            print("❌ Token lacks required permissions")
            print("   Response:", response.json().get('message', 'Unknown error'))
            return False
            
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print("   Response:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_cisco_github_repositories():
    """Test Cisco GitHub Enterprise repository access."""
    print("\n📁 Testing Repository Access...")
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    github_host = os.getenv("GITHUB_HOST", "https://wwwin-github.cisco.com")
    
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    try:
        # Get user's repositories
        repos_url = f"{github_host}/api/v3/user/repos"
        response = requests.get(repos_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            repos = response.json()
            print(f"✅ Found {len(repos)} repositories")
            
            # Show first 5 repositories
            for repo in repos[:5]:
                print(f"   - {repo.get('full_name', 'Unknown')}: {repo.get('description', 'No description')}")
                print(f"     URL: {repo.get('html_url', 'Unknown')}")
            
            if len(repos) > 5:
                print(f"   ... and {len(repos) - 5} more repositories")
            
            return True
        else:
            print(f"❌ Failed to get repositories: {response.status_code}")
            print("   Response:", response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error getting repositories: {e}")
        return False

def test_cisco_github_organizations():
    """Test Cisco GitHub Enterprise organization access."""
    print("\n🏢 Testing Organization Access...")
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    github_host = os.getenv("GITHUB_HOST", "https://wwwin-github.cisco.com")
    
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    try:
        # Get user's organizations
        orgs_url = f"{github_host}/api/v3/user/orgs"
        response = requests.get(orgs_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            orgs = response.json()
            print(f"✅ Found {len(orgs)} organizations")
            
            # Show organizations
            for org in orgs:
                print(f"   - {org.get('login', 'Unknown')}: {org.get('description', 'No description')}")
            
            return True
        else:
            print(f"❌ Failed to get organizations: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting organizations: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Cisco GitHub Enterprise Validation Test")
    print("=" * 60)
    
    # Test 1: Basic token validation
    token_valid = test_cisco_github_token()
    
    if token_valid:
        # Test 2: Repository access
        repo_access = test_cisco_github_repositories()
        
        # Test 3: Organization access
        org_access = test_cisco_github_organizations()
        
        # Summary
        print("\n📊 Test Results Summary:")
        print("=" * 50)
        print(f"✅ Token Validation: {'PASS' if token_valid else 'FAIL'}")
        print(f"✅ Repository Access: {'PASS' if repo_access else 'FAIL'}")
        print(f"✅ Organization Access: {'PASS' if org_access else 'FAIL'}")
        
        if token_valid and repo_access:
            print("\n🎉 All tests passed! Your Cisco GitHub Enterprise token is working correctly.")
            print("   You can now use it with the LangGraph incident response system.")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
    else:
        print("\n❌ Token validation failed. Please create a new Cisco GitHub Enterprise Personal Access Token.")
        print("\n💡 How to create a new token:")
        print("   1. Go to https://wwwin-github.cisco.com/settings/tokens")
        print("   2. Click 'Generate new token'")
        print("   3. Set appropriate permissions for your repositories")
        print("   4. Copy the new token and update your .env file")

if __name__ == "__main__":
    main()
