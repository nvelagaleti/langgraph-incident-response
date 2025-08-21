#!/usr/bin/env python3
"""
Search repositories using incident keywords to find relevant repositories.
"""

import asyncio
import os
import httpx
from dotenv import load_dotenv

async def search_repos_by_incident():
    """Search repositories using incident keywords."""
    print("🔍 Searching repositories using incident keywords...")
    
    # Load environment variables
    load_dotenv()
    
    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    
    if not github_token:
        print("❌ GitHub token not found")
        return False
    
    print(f"✅ GitHub token found")
    
    # Incident keywords extracted from the description
    incident_keywords = [
        "UI", "web application", "product", "GraphQL", "service", 
        "frontend", "backend", "products", "microservices", "API"
    ]
    
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
                
                # Get all repositories for the authenticated user
                repos_url = "https://api.github.com/user/repos?per_page=100&sort=updated&type=all"
                repos_response = await client.get(repos_url, headers=headers, timeout=10.0)
                
                if repos_response.status_code == 200:
                    repos_data = repos_response.json()
                    print(f"✅ Found {len(repos_data)} total repositories")
                    
                    # Score repositories based on keyword matches
                    scored_repos = []
                    
                    for repo in repos_data:
                        repo_name = repo.get('name', '') or ''
                        repo_description = repo.get('description', '') or ''
                        repo_name = repo_name.lower()
                        repo_description = repo_description.lower()
                        repo_full_name = repo.get('full_name', '')
                        repo_private = repo.get('private', False)
                        repo_language = repo.get('language', 'Unknown')
                        
                        # Calculate relevance score
                        score = 0
                        matched_keywords = []
                        
                        for keyword in incident_keywords:
                            keyword_lower = keyword.lower()
                            if keyword_lower in repo_name:
                                score += 3  # High score for name match
                                matched_keywords.append(keyword)
                            elif keyword_lower in repo_description:
                                score += 2  # Medium score for description match
                                matched_keywords.append(keyword)
                        
                        if score > 0:
                            scored_repos.append({
                                'repo': repo,
                                'score': score,
                                'matched_keywords': list(set(matched_keywords))
                            })
                    
                    # Sort by score (highest first)
                    scored_repos.sort(key=lambda x: x['score'], reverse=True)
                    
                    print(f"\n🎯 Found {len(scored_repos)} relevant repositories:")
                    
                    for i, scored_repo in enumerate(scored_repos, 1):
                        repo = scored_repo['repo']
                        score = scored_repo['score']
                        matched_keywords = scored_repo['matched_keywords']
                        
                        repo_name = repo.get('name', 'Unknown')
                        repo_full_name = repo.get('full_name', 'Unknown')
                        repo_description = repo.get('description', 'No description')
                        repo_language = repo.get('language', 'Unknown')
                        repo_private = repo.get('private', False)
                        
                        visibility = "🔒 Private" if repo_private else "🌐 Public"
                        
                        print(f"\n   {i}. {repo_full_name} {visibility} (Score: {score})")
                        print(f"       Language: {repo_language}")
                        print(f"       Matched Keywords: {', '.join(matched_keywords)}")
                        if repo_description:
                            print(f"       Description: {repo_description}")
                    
                    # Return the top relevant repositories
                    relevant_repos = [scored_repo['repo']['full_name'] for scored_repo in scored_repos]
                    return relevant_repos
                    
                else:
                    print(f"❌ Failed to get repositories: {repos_response.status_code}")
                    print(f"Response: {repos_response.text}")
                    return False
            else:
                print(f"❌ Failed to authenticate: {user_response.status_code}")
                print(f"Response: {user_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error searching repositories: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(search_repos_by_incident())
