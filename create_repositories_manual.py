#!/usr/bin/env python3
"""
Create GitHub Repositories Manually
Create repositories using direct GitHub API calls
"""

import os
import requests
import json
from dotenv import load_dotenv

def create_repositories():
    """Create repositories on GitHub using direct API calls."""
    print("🔄 Creating GitHub Repositories Manually")
    print("=" * 50)
    
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not token:
        print("❌ No GitHub token found")
        return
    
    # Repository configurations
    repositories = [
        {
            "name": "productsBackendService",
            "description": "Backend service for products microservices architecture",
            "private": True
        },
        {
            "name": "productsGraphQLService",
            "description": "GraphQL service for products API",
            "private": True
        },
        {
            "name": "productsWebApp",
            "description": "Web application for products frontend",
            "private": True
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "LangGraph-Incident-Response/1.0"
    }
    
    # First, check token permissions
    print("🔍 Checking token permissions...")
    try:
        response = requests.get("https://api.github.com/user", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Authenticated as: {user_data.get('login')}")
            
            # Check scopes from headers
            scopes = response.headers.get('X-OAuth-Scopes', '')
            if scopes:
                print(f"📋 Token scopes: {scopes}")
            else:
                print("⚠️  No scopes information available")
                
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return
            
    except Exception as e:
        print(f"❌ Error checking permissions: {e}")
        return
    
    # Create repositories
    created_repos = []
    
    for repo in repositories:
        name = repo["name"]
        description = repo["description"]
        private = repo["private"]
        
        print(f"\n🔄 Creating repository: {name}")
        print(f"   Description: {description}")
        print(f"   Private: {private}")
        
        # Check if repository already exists
        check_url = f"https://api.github.com/repos/nvelagaleti/{name}"
        check_response = requests.get(check_url, headers=headers)
        
        if check_response.status_code == 200:
            print(f"   ⚠️  Repository already exists: {name}")
            repo_data = check_response.json()
            clone_url = repo_data.get('clone_url')
            html_url = repo_data.get('html_url')
            created_repos.append({
                "name": name,
                "clone_url": clone_url,
                "html_url": html_url,
                "exists": True
            })
            continue
        
        # Create new repository
        create_data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": False
        }
        
        try:
            response = requests.post(
                "https://api.github.com/user/repos",
                headers=headers,
                json=create_data
            )
            
            if response.status_code == 201:
                repo_data = response.json()
                clone_url = repo_data.get('clone_url')
                html_url = repo_data.get('html_url')
                
                print(f"   ✅ Repository created successfully!")
                print(f"   🌐 URL: {html_url}")
                print(f"   🔗 Clone URL: {clone_url}")
                
                created_repos.append({
                    "name": name,
                    "clone_url": clone_url,
                    "html_url": html_url,
                    "exists": False
                })
                
            elif response.status_code == 403:
                print(f"   ❌ Permission denied (403)")
                print(f"   📄 Response: {response.text}")
                print(f"   💡 Token needs 'repo' scope to create repositories")
                
            else:
                print(f"   ❌ Error creating repository: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print(f"\n📊 Repository Creation Summary:")
    print("=" * 50)
    
    if created_repos:
        for repo in created_repos:
            status = "✅ Created" if not repo.get("exists") else "⚠️  Already exists"
            print(f"{status}: {repo['name']}")
            print(f"   URL: {repo['html_url']}")
            print(f"   Clone: {repo['clone_url']}")
            print()
    else:
        print("❌ No repositories were created")
    
    # Next steps
    print(f"📋 Next Steps:")
    print("=" * 30)
    
    if created_repos:
        print(f"1. Run git commands to push repositories:")
        for repo in created_repos:
            if not repo.get("exists"):
                local_path = f"../{repo['name']}"
                clone_url = repo['clone_url']
                print(f"\n   For {repo['name']}:")
                print(f"   cd {local_path}")
                print(f"   git remote add origin {clone_url}")
                print(f"   git branch -M master")
                print(f"   git push -u origin master")
    else:
        print(f"1. Update your GitHub token with 'repo' scope")
        print(f"2. Re-run this script")
    
    print(f"\n2. Test the incident response system with the new repositories")

if __name__ == "__main__":
    create_repositories()
