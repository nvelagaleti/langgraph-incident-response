#!/usr/bin/env python3
"""
Simple script to get all repositories in your GitHub account.
"""

import asyncio
import os
import httpx
from dotenv import load_dotenv

async def get_my_repos():
    """Get all repositories in your GitHub account."""
    print("🔍 Getting all repositories in your GitHub account...")
    
    # Load environment variables
    load_dotenv()
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not github_token:
        print("❌ GitHub token not found")
        return False
    
    print(f"✅ GitHub token found")
    
    try:
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with httpx.AsyncClient() as client:
            # Get user info first
            user_response = await client.get("https://api.github.com/user", headers=headers, timeout=10.0)
            
            if user_response.status_code == 200:
                user_data = user_response.json()
                username = user_data.get('login', 'unknown')
                print(f"✅ Authenticated as: {username}")
                
                # Get all repositories for the user
                repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
                repos_response = await client.get(repos_url, headers=headers, timeout=10.0)
                
                if repos_response.status_code == 200:
                    repos_data = repos_response.json()
                    print(f"✅ Found {len(repos_data)} repositories:")
                    
                    for i, repo in enumerate(repos_data, 1):
                        repo_name = repo.get('name', 'Unknown')
                        repo_full_name = repo.get('full_name', 'Unknown')
                        repo_description = repo.get('description', 'No description')
                        repo_language = repo.get('language', 'Unknown')
                        repo_stars = repo.get('stargazers_count', 0)
                        
                        print(f"   {i:2d}. {repo_full_name}")
                        print(f"       Language: {repo_language}")
                        print(f"       Stars: {repo_stars}")
                        if repo_description:
                            print(f"       Description: {repo_description}")
                        print()
                    
                    return repos_data
                else:
                    print(f"❌ Failed to get repositories: {repos_response.status_code}")
                    print(f"Response: {repos_response.text}")
                    return False
            else:
                print(f"❌ Failed to authenticate: {user_response.status_code}")
                print(f"Response: {user_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error getting repositories: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(get_my_repos())
