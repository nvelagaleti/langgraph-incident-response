#!/usr/bin/env python3
"""
Debug Step 1 functionality to see why incident details are not found.
"""

import asyncio
import os
from dotenv import load_dotenv

async def debug_step1():
    """Debug Step 1 functionality."""
    print("🔍 Debugging Step 1: Incident Details Fetching")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Test incident IDs
    test_incident_ids = ["IR-1", "IR-7", "IR-6", "IR-5"]
    
    try:
        from jira_mcp_complete_integration import JiraMCPCompleteIntegration
        
        # Initialize Jira client
        print("🔧 Initializing Jira client...")
        jira_client = JiraMCPCompleteIntegration()
        await jira_client.initialize()
        print("✅ Jira client initialized")
        
        for incident_id in test_incident_ids:
            print(f"\n🔍 Testing incident ID: {incident_id}")
            print("-" * 40)
            
            # Try different JQL queries
            jql_queries = [
                f'issuekey = "{incident_id}"',
                f'issuekey = {incident_id}',
                f'key = "{incident_id}"',
                f'project = IR AND issuekey = "{incident_id}"'
            ]
            
            for jql_query in jql_queries:
                try:
                    print(f"   Testing JQL: {jql_query}")
                    jira_issues = await jira_client.search_issues(
                        jql=jql_query,
                        max_results=1
                    )
                    
                    if jira_issues and len(jira_issues) > 0:
                        print(f"   ✅ Found {len(jira_issues)} issues")
                        issue = jira_issues[0]
                        print(f"   📋 Issue Key: {issue.get('key', 'N/A')}")
                        print(f"   📋 Summary: {issue.get('fields', {}).get('summary', 'N/A')}")
                        break
                    else:
                        print(f"   ❌ No issues found")
                        
                except Exception as e:
                    print(f"   ❌ Error with JQL '{jql_query}': {e}")
            
            print()
    
    except Exception as e:
        print(f"❌ Error initializing Jira client: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_step1())
