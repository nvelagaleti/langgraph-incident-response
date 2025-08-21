#!/usr/bin/env python3
"""
Update Commit Messages
Safely rewrite commit history to update prefixes without code loss
"""

import os
import subprocess
import sys

def update_commit_messages():
    """Update commit message prefixes for each repository."""
    print("🔄 Updating Commit Message Prefixes")
    print("=" * 50)
    
    # Repository configurations
    repositories = [
        {
            "path": "../productsBackendService",
            "old_prefix": "MYAPP",
            "new_prefix": "MYAPPBE",
            "name": "Backend Service"
        },
        {
            "path": "../productsGraphQLService",
            "old_prefix": "MYAPP", 
            "new_prefix": "MYAPPGQL",
            "name": "GraphQL Service"
        }
    ]
    
    for repo in repositories:
        path = repo["path"]
        old_prefix = repo["old_prefix"]
        new_prefix = repo["new_prefix"]
        name = repo["name"]
        
        print(f"\n🔄 Processing {name}: {path}")
        print(f"   Old prefix: {old_prefix}")
        print(f"   New prefix: {new_prefix}")
        
        # Check if repository exists
        if not os.path.exists(path):
            print(f"   ❌ Repository path does not exist: {path}")
            continue
        
        # Check if it's a git repository
        git_path = os.path.join(path, ".git")
        if not os.path.exists(git_path):
            print(f"   ❌ Not a git repository: {path}")
            continue
        
        print(f"   ✅ Repository found")
        
        # Show current commits
        print(f"   📋 Current commits:")
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                for commit in commits:
                    if commit:
                        print(f"      {commit}")
            else:
                print(f"      ❌ Error getting commits: {result.stderr}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
        
        # Create git filter-branch command
        filter_command = f'git filter-branch --msg-filter \'sed "s/{old_prefix}-/{new_prefix}-/g"\' -- --all'
        
        print(f"\n   🔧 Git command to run:")
        print(f"   =========================")
        print(f"   cd {path}")
        print(f"   {filter_command}")
        print(f"   =========================")
        
        # Ask for confirmation
        print(f"\n   ⚠️  WARNING: This will rewrite commit history!")
        print(f"   💡 Make sure you have a backup before proceeding.")
        print(f"   🎯 This will update all commit messages from '{old_prefix}-' to '{new_prefix}-'")
        
        # Show what will change
        print(f"\n   📝 Example changes:")
        print(f"      Before: {old_prefix}-7: Implement user-friendly error handling")
        print(f"      After:  {new_prefix}-7: Implement user-friendly error handling")
        
        print(f"   ✅ Repository {name} ready for commit message update")
    
    print(f"\n🎉 Commit message update plan complete!")
    print(f"📋 Next steps:")
    print(f"   1. Run the git filter-branch commands shown above for each repository")
    print(f"   2. Verify the commit messages are updated correctly")
    print(f"   3. Then proceed with repository duplication")
    print(f"\n⚠️  Important Notes:")
    print(f"   - This rewrites git history, so make sure you have backups")
    print(f"   - All code and changes will be preserved")
    print(f"   - Only the commit message prefixes will change")
    print(f"   - Run this BEFORE duplicating to GitHub")

def show_safe_alternative():
    """Show a safer alternative approach."""
    print(f"\n🛡️  SAFER ALTERNATIVE APPROACH")
    print(f"=" * 50)
    print(f"If you prefer not to rewrite history, you can:")
    print(f"1. Duplicate repositories as-is with current commit messages")
    print(f"2. Create new commits with updated prefixes going forward")
    print(f"3. This preserves original history while using new prefixes")
    print(f"\nWould you like to:")
    print(f"   A) Rewrite history with new prefixes (current plan)")
    print(f"   B) Keep current history and use new prefixes going forward")

if __name__ == "__main__":
    update_commit_messages()
    show_safe_alternative()
