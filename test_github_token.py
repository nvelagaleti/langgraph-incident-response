#!/usr/bin/env python3
"""
Simple GitHub Token Test Script
Tests if your GitHub Personal Access Token is valid and working.
"""

import os
import requests
from dotenv import load_dotenv

def test_github_token():
    """Test GitHub Personal Access Token."""
    print("🔑 GitHub Token Test")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get token from environment
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        print("❌ No GitHub token found in .env file")
        print("   Set GITHUB_PERSONAL_ACCESS_TOKEN in your .env file")
        return False
    
    print(f"✅ Token found: {token[:10]}...")
    
    # Test GitHub API
    print("\n🔗 Testing GitHub API...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # Test user endpoint
        response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Token is valid!")
            print(f"   User: {user_data.get('login', 'Unknown')}")
            print(f"   Name: {user_data.get('name', 'Unknown')}")
            print(f"   Email: {user_data.get('email', 'Unknown')}")
            print(f"   Public repos: {user_data.get('public_repos', 'Unknown')}")
            
            # Test rate limit
            rate_limit_response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
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

def test_github_repositories():
    """Test GitHub repository access."""
    print("\n📁 Testing Repository Access...")
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        return False
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # Get user's repositories
        response = requests.get("https://api.github.com/user/repos", headers=headers, timeout=10)
        
        if response.status_code == 200:
            repos = response.json()
            print(f"✅ Found {len(repos)} repositories")
            
            # Show first 5 repositories
            for repo in repos[:5]:
                print(f"   - {repo.get('full_name', 'Unknown')}: {repo.get('description', 'No description')}")
            
            if len(repos) > 5:
                print(f"   ... and {len(repos) - 5} more repositories")
            
            return True
        else:
            print(f"❌ Failed to get repositories: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting repositories: {e}")
        return False

def test_github_commit_access():
    """Test GitHub commit access."""
    print("\n📝 Testing Commit Access...")
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        return False
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # Test with a public repository (GitHub's own repo)
        response = requests.get(
            "https://api.github.com/repos/github/github-mcp-server/commits",
            headers=headers,
            params={"per_page": 1},
            timeout=10
        )
        
        if response.status_code == 200:
            commits = response.json()
            if commits:
                commit = commits[0]
                print("✅ Commit access successful!")
                print(f"   Latest commit: {commit.get('sha', 'Unknown')[:8]}")
                print(f"   Author: {commit.get('commit', {}).get('author', {}).get('name', 'Unknown')}")
                print(f"   Message: {commit.get('commit', {}).get('message', 'Unknown')[:50]}...")
                return True
            else:
                print("❌ No commits found")
                return False
        else:
            print(f"❌ Failed to get commits: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting commits: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 GitHub Token Validation Test")
    print("=" * 50)
    
    # Test 1: Basic token validation
    token_valid = test_github_token()
    
    if token_valid:
        # Test 2: Repository access
        repo_access = test_github_repositories()
        
        # Test 3: Commit access
        commit_access = test_github_commit_access()
        
        # Summary
        print("\n📊 Test Results Summary:")
        print("=" * 50)
        print(f"✅ Token Validation: {'PASS' if token_valid else 'FAIL'}")
        print(f"✅ Repository Access: {'PASS' if repo_access else 'FAIL'}")
        print(f"✅ Commit Access: {'PASS' if commit_access else 'FAIL'}")
        
        if token_valid and repo_access and commit_access:
            print("\n🎉 All tests passed! Your GitHub token is working correctly.")
            print("   You can now use it with the LangGraph incident response system.")
        else:
            print("\n⚠️  Some tests failed. Check the output above for details.")
    else:
        print("\n❌ Token validation failed. Please create a new GitHub Personal Access Token.")
        print("\n💡 How to create a new token:")
        print("   1. Go to GitHub Settings → Developer settings → Personal access tokens")
        print("   2. Click 'Fine-grained tokens' → 'Generate new token'")
        print("   3. Set repository access and permissions")
        print("   4. Copy the new token and update your .env file")

if __name__ == "__main__":
    main()
