#!/usr/bin/env python3
"""
Test Step 1 functionality with a specific incident ID.
"""

import asyncio
import os
from dotenv import load_dotenv

async def test_step1():
    """Test Step 1 functionality."""
    print("🧪 Testing Step 1: Incident Details Fetching")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Test with IR-1 (the main incident)
    incident_id = "IR-1"
    print(f"🔍 Testing with incident ID: {incident_id}")
    
    try:
        from jira_mcp_complete_integration import JiraMCPCompleteIntegration
        
        # Initialize Jira client (same as Step 1)
        print("🔧 Initializing Jira client...")
        jira_client = JiraMCPCompleteIntegration()
        await jira_client.initialize()
        print("✅ Jira client initialized")
        
        # Use the exact same JQL query as Step 1
        jql_query = f'issuekey = "{incident_id}"'
        print(f"🔍 Using JQL: {jql_query}")
        
        # Search for the incident
        jira_issues = await jira_client.search_issues(
            jql=jql_query,
            max_results=1
        )
        
        if not jira_issues or len(jira_issues) == 0:
            print(f"❌ Incident {incident_id} not found in Jira")
            return False
        else:
            print(f"✅ Found {len(jira_issues)} issues")
            
            # Extract incident details (same as Step 1)
            jira_issue = jira_issues[0]
            print(f"🔍 Debug: Jira issue structure: {list(jira_issue.keys())}")
            fields = jira_issue.get('fields', {})
            print(f"🔍 Debug: Fields available: {list(fields.keys())}")
            
            # Handle description which might be in Atlassian Document Format
            description = fields.get('description', '')
            if isinstance(description, dict) and 'content' in description:
                # Extract text from Atlassian Document Format
                content_parts = []
                for content in description.get('content', []):
                    if 'content' in content:
                        for text_content in content['content']:
                            if text_content.get('type') == 'text':
                                content_parts.append(text_content.get('text', ''))
                description = ' '.join(content_parts)
            
            # Get priority name safely
            priority_obj = fields.get('priority', {})
            priority_name = priority_obj.get('name', 'Medium') if isinstance(priority_obj, dict) else 'Medium'
            
            # Get assignee name safely
            assignee_obj = fields.get('assignee', {})
            assignee_name = assignee_obj.get('displayName', 'Unassigned') if isinstance(assignee_obj, dict) else 'Unassigned'
            
            # Get reporter name safely
            reporter_obj = fields.get('reporter', {})
            reporter_name = reporter_obj.get('displayName', 'Unknown') if isinstance(reporter_obj, dict) else 'Unknown'
            
            incident_details = {
                'title': fields.get('summary', f'Incident {incident_id}'),
                'description': description,
                'severity': priority_name.lower(),
                'status': 'open',
                'error_message': description,
                'affected_components': [fields.get('environment', 'unknown')],
                'user_impact': description,
                'jira_issue_key': jira_issue.get('key', incident_id),
                'jira_issue_id': jira_issue.get('id', ''),
                'created': jira_issue.get('created', ''),
                'updated': jira_issue.get('updated', ''),
                'assignee': assignee_name,
                'reporter': reporter_name,
                'labels': fields.get('labels', []),
                'priority': priority_name
            }
            
            print(f"✅ Successfully extracted incident details:")
            print(f"   📋 Title: {incident_details['title']}")
            print(f"   📋 Description: {incident_details['description'][:100]}...")
            print(f"   📋 Severity: {incident_details['severity']}")
            print(f"   📋 Status: {incident_details['status']}")
            print(f"   📋 Assignee: {incident_details['assignee']}")
            print(f"   📋 Reporter: {incident_details['reporter']}")
            
            return True
    
    except Exception as e:
        print(f"❌ Error in Step 1 test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_step1())
    if success:
        print("\n🎉 Step 1 test completed successfully!")
        print("💡 Try using 'IR-1' as the incident ID in LangGraph Studio")
    else:
        print("\n❌ Step 1 test failed!")
