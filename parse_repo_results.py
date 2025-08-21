#!/usr/bin/env python3
"""
Parse Repository Results
Simple script to parse and display the repository search results
"""

import json

# From the previous search results
repo_search_result = '''{"total_count":1,"incomplete_results":false,"items":[{"id":1041645940,"node_id":"R_kgDOPhZBdA","owner":{"login":"nvelagaleti","id":11649784,"node_id":"MDQ6VXNlcjExNjQ5Nzg0","avatar_url":"https://avatars.githubusercontent.com/u/11649784?v=4","html_url":"https://github.com/nvelagaleti","gravatar_id":"","type":"User","site_admin":false},"name":"my-ai-agent","full_name":"nvelagaleti/my-ai-agent","private":false,"description":"AI agent built with LangGraph and FastAPI","language":"Python","stargazers_count":0,"watchers_count":0,"forks_count":0,"default_branch":"main","created_at":"2024-12-12T17:28:16Z","updated_at":"2024-12-12T17:30:09Z"}]}'''

def parse_repositories():
    """Parse and display repository information."""
    print("📁 Your GitHub Repositories")
    print("=" * 50)
    
    try:
        data = json.loads(repo_search_result)
        total_count = data.get('total_count', 0)
        items = data.get('items', [])
        
        print(f"✅ Found {total_count} public repository")
        
        for i, repo in enumerate(items, 1):
            print(f"\n📁 Repository {i}:")
            print(f"   📝 Name: {repo.get('name', 'Unknown')}")
            print(f"   🔗 Full Name: {repo.get('full_name', 'Unknown')}")
            print(f"   📄 Description: {repo.get('description', 'No description')}")
            print(f"   🌐 URL: https://github.com/{repo.get('full_name', '')}")
            print(f"   🐍 Language: {repo.get('language', 'Unknown')}")
            print(f"   ⭐ Stars: {repo.get('stargazers_count', 0)}")
            print(f"   🍴 Forks: {repo.get('forks_count', 0)}")
            print(f"   🔒 Private: {repo.get('private', False)}")
            print(f"   🌿 Default Branch: {repo.get('default_branch', 'main')}")
            print(f"   📅 Created: {repo.get('created_at', 'Unknown')}")
            print(f"   🔄 Updated: {repo.get('updated_at', 'Unknown')}")
            
        # Summary for incident response
        print(f"\n🚀 Summary for Incident Response System:")
        print("=" * 50)
        
        if items:
            repo = items[0]  # First (and only) repository
            repo_name = repo.get('name')
            repo_full_name = repo.get('full_name')
            default_branch = repo.get('default_branch', 'main')
            
            print(f"✅ Repository available for monitoring: {repo_full_name}")
            print(f"✅ Default branch: {default_branch}")
            print(f"✅ Language: {repo.get('language', 'Unknown')}")
            
            print(f"\n🔧 Configuration for LangGraph System:")
            print(f"   GITHUB_REPO_OWNER=nvelagaleti")
            print(f"   GITHUB_REPO_NAME={repo_name}")
            print(f"   GITHUB_DEFAULT_BRANCH={default_branch}")
            
            print(f"\n📋 Available for incident response:")
            print(f"   - Monitor commits on {default_branch} branch")
            print(f"   - Analyze file changes and diffs")
            print(f"   - Create issues for incidents")
            print(f"   - Track incident resolution")
            
        else:
            print("❌ No repositories found for incident monitoring")
            
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing repository data: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    parse_repositories()
