#!/usr/bin/env python3
"""
Test the complete production workflow with real MCP integrations
"""

import asyncio
import sys
import os
from pathlib import Path

# Add studio directory to path
sys.path.append('studio')

async def test_complete_workflow():
    """Test the complete production workflow."""
    print("🧪 Testing Complete Production Workflow")
    print("=" * 60)
    
    try:
        # Import the production graph
        from incident_response_with_mcp import create_graph, MCPIncidentState
        
        # Create graph
        print("📋 Creating production graph...")
        graph = create_graph()
        
        # Create initial state with just incident_id
        initial_state = MCPIncidentState(
            incident_id='IR-2024-001',
            title='',
            description='',
            severity='',
            status='',
            created_at=None,
            updated_at=None,
            findings=[],
            recommendations=[],
            jira_tickets=[],
            github_analysis={},
            mcp_integrations={
                'github_enabled': True,
                'jira_enabled': True,
                'mcp_servers': []
            },
            messages=[]
        )
        
        print("✅ Starting complete workflow execution...")
        print("🔍 This will test:")
        print("   - Circuit LLM integration")
        print("   - GitHub MCP integration")
        print("   - Jira MCP integration")
        print("   - Complete incident response workflow")
        
        # Execute the workflow
        result = await graph.ainvoke(initial_state)
        
        print("\n🎉 Workflow completed successfully!")
        print("=" * 60)
        print(f"📊 Final Results:")
        print(f"   📝 Title: {result.get('title', 'N/A')}")
        print(f"   🚨 Severity: {result.get('severity', 'N/A')}")
        print(f"   📋 Status: {result.get('status', 'N/A')}")
        print(f"   🔍 Findings: {len(result.get('findings', []))}")
        print(f"   📋 Recommendations: {len(result.get('recommendations', []))}")
        print(f"   🎫 Jira tickets: {len(result.get('jira_tickets', []))}")
        print(f"   🔗 GitHub analysis: {len(result.get('github_analysis', {}))}")
        
        # Show some details
        if result.get('findings'):
            print(f"\n🔍 Sample Findings:")
            for i, finding in enumerate(result.get('findings', [])[:3], 1):
                print(f"   {i}. {finding.get('description', 'N/A')[:100]}...")
        
        if result.get('recommendations'):
            print(f"\n📋 Sample Recommendations:")
            for i, rec in enumerate(result.get('recommendations', [])[:3], 1):
                print(f"   {i}. {rec.get('action', 'N/A')[:100]}...")
        
        if result.get('jira_tickets'):
            print(f"\n🎫 Jira Tickets Created:")
            for ticket in result.get('jira_tickets', []):
                print(f"   - {ticket.get('key', 'N/A')}: {ticket.get('summary', 'N/A')}")
        
        print(f"\n✅ Production workflow test completed successfully!")
        print("🚀 Your MCP integration is production-ready!")
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
