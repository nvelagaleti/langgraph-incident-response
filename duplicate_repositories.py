#!/usr/bin/env python3
"""
Duplicate Repositories to Personal GitHub
Create new repositories in personal GitHub space while preserving commit history
"""

import os
import asyncio
import subprocess
import json
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

async def duplicate_repositories():
    """Duplicate repositories to personal GitHub space."""
    print("🔄 Duplicating Repositories to Personal GitHub")
    print("=" * 60)
    
    load_dotenv()
    
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    mcp_url = "https://api.githubcopilot.com/mcp"
    
    if not token:
        print("❌ No GitHub token found")
        return
    
    # Repositories to duplicate
    repositories = [
        {
            "local_path": "../productsBackendService",
            "new_name": "productsBackendService",
            "description": "Backend service for products microservices architecture"
        },
        {
            "local_path": "../productsGraphQLService", 
            "new_name": "productsGraphQLService",
            "description": "GraphQL service for products API"
        },
        {
            "local_path": "../productsWebApp",
            "new_name": "productsWebApp", 
            "description": "Web application for products frontend"
        }
    ]
    
    try:
        # Configure MCP client
        servers_config = {
            "github": {
                "transport": "streamable_http",
                "url": mcp_url,
                "headers": {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json",
                    "User-Agent": "LangGraph-Incident-Response/1.0"
                }
            }
        }
        
        client = MultiServerMCPClient(servers_config)
        tools = await client.get_tools()
        
        # Find create_repository tool
        create_repo_tool = None
        for tool in tools:
            if hasattr(tool, 'name') and tool.name == 'create_repository':
                create_repo_tool = tool
                break
        
        if not create_repo_tool:
            print("❌ create_repository tool not found")
            return
        
        print("✅ MCP client configured")
        print(f"✅ Found create_repository tool: {create_repo_tool.name}")
        
        # Process each repository
        for repo_info in repositories:
            local_path = repo_info["local_path"]
            new_name = repo_info["new_name"]
            description = repo_info["description"]
            
            print(f"\n🔄 Processing: {local_path}")
            print(f"   New name: {new_name}")
            print(f"   Description: {description}")
            
            # Check if local repository exists
            if not os.path.exists(local_path):
                print(f"   ❌ Local path does not exist: {local_path}")
                continue
            
            # Check if it's a git repository
            git_path = os.path.join(local_path, ".git")
            if not os.path.exists(git_path):
                print(f"   ❌ Not a git repository: {local_path}")
                continue
            
            print(f"   ✅ Local repository found")
            
            # Step 1: Create new repository on GitHub
            print(f"   🔧 Creating repository on GitHub...")
            try:
                create_result = await create_repo_tool.ainvoke({
                    "name": new_name,
                    "description": description,
                    "private": True,
                    "auto_init": False
                })
                
                print(f"   ✅ Repository created on GitHub")
                print(f"   📄 Result: {str(create_result)[:200]}...")
                
                # Parse the result to get the repository URL
                try:
                    repo_data = json.loads(create_result)
                    repo_url = repo_data.get('html_url', f"https://github.com/nvelagaleti/{new_name}")
                    clone_url = repo_data.get('clone_url', f"https://github.com/nvelagaleti/{new_name}.git")
                except:
                    repo_url = f"https://github.com/nvelagaleti/{new_name}"
                    clone_url = f"https://github.com/nvelagaleti/{new_name}.git"
                
                print(f"   🌐 Repository URL: {repo_url}")
                print(f"   🔗 Clone URL: {clone_url}")
                
            except Exception as e:
                print(f"   ❌ Error creating repository: {e}")
                continue
            
            # Step 2: Prepare git commands for the user
            print(f"   📋 Git commands to run:")
            print(f"   =========================")
            print(f"   cd {local_path}")
            print(f"   git remote add origin {clone_url}")
            print(f"   git branch -M master")
            print(f"   git push -u origin master")
            print(f"   =========================")
            
            # Step 3: Check current git status
            print(f"   🔍 Checking current git status...")
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=local_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    if result.stdout.strip():
                        print(f"   ⚠️  Uncommitted changes detected:")
                        print(f"   {result.stdout}")
                        print(f"   💡 Consider committing changes before pushing")
                    else:
                        print(f"   ✅ Repository is clean (no uncommitted changes)")
                else:
                    print(f"   ❌ Error checking git status: {result.stderr}")
                    
            except Exception as e:
                print(f"   ❌ Error running git status: {e}")
            
            print(f"   ✅ Repository {new_name} ready for duplication")
        
        print(f"\n🎉 Repository duplication setup complete!")
        print(f"📋 Next steps:")
        print(f"   1. Run the git commands shown above for each repository")
        print(f"   2. Verify repositories are created on GitHub")
        print(f"   3. Test the incident response system with the new repositories")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(duplicate_repositories())
