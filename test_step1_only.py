#!/usr/bin/env python3
"""
Test only Step 1 of the incident response workflow with fresh Jira tokens
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the enhanced incident response module
from studio.incident_response_enhanced import step1_parse_ir_ticket, IncidentInput, IncidentState

# Test incident ID
TEST_INCIDENT_ID = "IR-001"

async def test_step1_only():
    """Test only Step 1: Parse IR ticket and fetch from Jira MCP"""
    print("🧪 TESTING STEP 1 ONLY: Parse IR Ticket with Fresh Jira Tokens")
    print("="*70)
    
    # Create initial state with just incident_id
    initial_state = IncidentInput(incident_id=TEST_INCIDENT_ID)
    
    try:
        # Run step 1
        result = await step1_parse_ir_ticket(initial_state)
        
        print(f"✅ Step 1 completed successfully!")
        print(f"📋 Incident Title: {result.get('title', 'N/A')}")
        print(f"📝 Description: {result.get('description', 'N/A')[:100]}...")
        print(f"🚨 Severity: {result.get('severity', 'N/A')}")
        print(f"📊 Status: {result.get('status', 'N/A')}")
        print(f"🔍 Jira Issue Key: {result.get('jira_issue_key', 'N/A')}")
        print(f"🔍 Jira Issue ID: {result.get('jira_issue_id', 'N/A')}")
        print(f"📚 GitHub Analysis Repos: {result.get('github_analysis', {}).get('repositories_to_check', [])}")
        print(f"✅ Completed Steps: {result.get('completed_steps', [])}")
        
        # Check MCP integrations
        mcp_integrations = result.get('mcp_integrations', {})
        print(f"🔗 GitHub Enabled: {mcp_integrations.get('github_enabled', False)}")
        print(f"🔗 Jira Enabled: {mcp_integrations.get('jira_enabled', False)}")
        
        # Show GitHub analysis details
        github_analysis = result.get('github_analysis', {})
        if github_analysis:
            print(f"\n🔍 GitHub Analysis Details:")
            print(f"   📚 Repositories to check: {github_analysis.get('repositories_to_check', [])}")
            print(f"   🎯 Analysis focus: {github_analysis.get('analysis_focus', 'N/A')}")
            print(f"   ⏰ Timeframe hours: {github_analysis.get('timeframe_hours', 'N/A')}")
            print(f"   🔍 Potential root causes: {github_analysis.get('potential_root_causes', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_step1_only())
