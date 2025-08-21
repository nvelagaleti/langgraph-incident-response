#!/usr/bin/env python3
"""
Test script for multi-repository GitHub MCP functionality.
"""

import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.services.mcp_client import mcp_client


async def test_multi_repo_setup():
    """Test multi-repository setup and configuration."""
    print("🔍 Testing Multi-Repository GitHub MCP Setup...")
    
    # Load environment variables
    load_dotenv()
    
    github_token = os.getenv("GITHUB_TOKEN")
    github_repos = os.getenv("GITHUB_REPOSITORIES")
    
    if not github_token:
        print("❌ GitHub token not found in environment")
        print("   Set GITHUB_TOKEN in your .env file")
        return False
    
    if not github_repos:
        print("❌ GitHub repositories not configured")
        print("   Set GITHUB_REPOSITORIES in your .env file")
        print("   Format: owner1/repo1,owner2/repo2,owner3/repo3")
        return False
    
    print(f"✅ GitHub token found")
    print(f"✅ GitHub repositories configured: {github_repos}")
    
    # Parse repositories
    repositories = []
    for repo in github_repos.split(","):
        repo = repo.strip()
        if "/" in repo:
            owner, name = repo.split("/", 1)
            repositories.append({"owner": owner, "name": name})
            print(f"   📁 {owner}/{name}")
        else:
            print(f"   ⚠️  Invalid repository format: {repo}")
    
    if not repositories:
        print("❌ No valid repositories found")
        return False
    
    return repositories


async def test_multi_repo_connections(repositories):
    """Test connections to multiple repositories."""
    print(f"\n🔗 Testing connections to {len(repositories)} repositories...")
    
    try:
        # Initialize MCP client for multi-repo support
        await mcp_client.initialize_github_mcp(github_token=os.getenv("GITHUB_TOKEN"))
        
        successful_connections = 0
        
        for repo in repositories:
            owner = repo["owner"]
            name = repo["name"]
            
            try:
                # Test connection to this repository
                session = await mcp_client.get_repo_session(owner, name)
                
                if session:
                    print(f"   ✅ Connected to {owner}/{name}")
                    successful_connections += 1
                else:
                    print(f"   ❌ Failed to connect to {owner}/{name}")
                    
            except Exception as e:
                print(f"   ❌ Error connecting to {owner}/{name}: {e}")
        
        print(f"\n📊 Connection Results: {successful_connections}/{len(repositories)} successful")
        return successful_connections == len(repositories)
        
    except Exception as e:
        print(f"❌ Error initializing multi-repo MCP client: {e}")
        return False


async def test_multi_repo_commit_analysis(repositories):
    """Test commit analysis across multiple repositories."""
    print(f"\n📊 Testing commit analysis across {len(repositories)} repositories...")
    
    try:
        # Get commits from the last 7 days
        until_date = datetime.now()
        since_date = until_date - timedelta(days=7)
        
        # Analyze commits from all repositories
        commits = await mcp_client.get_github_commits_multi_repo(
            since_date=since_date.isoformat(),
            until_date=until_date.isoformat(),
            repositories=repositories
        )
        
        print(f"✅ Found {len(commits)} total commits across all repositories")
        
        # Group commits by repository
        commits_by_repo = {}
        for commit in commits:
            repo = commit.repository
            if repo not in commits_by_repo:
                commits_by_repo[repo] = []
            commits_by_repo[repo].append(commit)
        
        # Display summary by repository
        print("\n📋 Commit Summary by Repository:")
        for repo, repo_commits in commits_by_repo.items():
            print(f"   📁 {repo}: {len(repo_commits)} commits")
            
            # Show recent commits
            recent_commits = sorted(repo_commits, key=lambda x: x.date, reverse=True)[:3]
            for commit in recent_commits:
                print(f"      - {commit.sha[:8]} by {commit.author}: {commit.message[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing commits: {e}")
        return False


async def test_cross_repo_correlation(repositories):
    """Test cross-repository correlation analysis."""
    print(f"\n🔗 Testing cross-repository correlation...")
    
    try:
        # Get commits from the last 24 hours for correlation
        until_date = datetime.now()
        since_date = until_date - timedelta(days=1)
        
        all_commits = []
        for repo in repositories:
            commits = await mcp_client.get_github_commits(
                since_date=since_date.isoformat(),
                until_date=until_date.isoformat(),
                repo_owner=repo["owner"],
                repo_name=repo["name"]
            )
            all_commits.extend(commits)
        
        if not all_commits:
            print("   ℹ️  No commits found in the last 24 hours")
            return True
        
        # Analyze commit patterns across repositories
        authors = set()
        commit_times = []
        
        for commit in all_commits:
            authors.add(commit.author)
            commit_times.append(commit.date)
        
        print(f"   👥 Authors across repositories: {', '.join(authors)}")
        print(f"   📅 Commit time range: {min(commit_times)} to {max(commit_times)}")
        
        # Look for related changes
        print("\n   🔍 Cross-repository analysis:")
        for repo in repositories:
            repo_commits = [c for c in all_commits if c.repository == f"{repo['owner']}/{repo['name']}"]
            if repo_commits:
                print(f"      📁 {repo['owner']}/{repo['name']}: {len(repo_commits)} commits")
                
                # Check for configuration or dependency changes
                config_changes = [c for c in repo_commits if any(keyword in c.message.lower() 
                                                              for keyword in ['config', 'dependency', 'version', 'update'])]
                if config_changes:
                    print(f"         ⚙️  {len(config_changes)} configuration/dependency changes detected")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in cross-repo correlation: {e}")
        return False


async def main():
    """Main test function."""
    print("🧪 Multi-Repository GitHub MCP Test")
    print("=" * 50)
    
    # Test 1: Setup and configuration
    repositories = await test_multi_repo_setup()
    if not repositories:
        print("\n❌ Multi-repo setup failed")
        return
    
    # Test 2: Repository connections
    connections_ok = await test_multi_repo_connections(repositories)
    if not connections_ok:
        print("\n❌ Repository connections failed")
        return
    
    # Test 3: Commit analysis
    analysis_ok = await test_multi_repo_commit_analysis(repositories)
    if not analysis_ok:
        print("\n❌ Commit analysis failed")
        return
    
    # Test 4: Cross-repo correlation
    correlation_ok = await test_cross_repo_correlation(repositories)
    if not correlation_ok:
        print("\n❌ Cross-repo correlation failed")
        return
    
    # Summary
    print("\n🎉 Multi-Repository GitHub MCP Test Results:")
    print("=" * 50)
    print("✅ Setup and configuration: PASS")
    print("✅ Repository connections: PASS")
    print("✅ Commit analysis: PASS")
    print("✅ Cross-repo correlation: PASS")
    print("\n🚀 Multi-repository support is working correctly!")
    
    # Cleanup
    await mcp_client.close()


if __name__ == "__main__":
    asyncio.run(main())
