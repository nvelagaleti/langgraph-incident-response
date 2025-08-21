"""
Enhanced Main Entry Point for LangGraph Incident Response System.
Demonstrates the enhanced agent with GitHub and Jira MCP integration.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv

from .graphs.enhanced_main_graph import EnhancedIncidentResponseGraph
from .types.state import IncidentSeverity, IncidentStatus


# Load environment variables
load_dotenv()


async def demonstrate_enhanced_incident_response():
    """
    Demonstrate the enhanced incident response system with GitHub and Jira MCP integration.
    """
    
    print("🚀 Enhanced LangGraph Incident Response System Demo")
    print("=" * 70)
    print("🔗 Integrated with GitHub and Jira MCP")
    print("=" * 70)
    
    # Create the enhanced incident response graph
    incident_graph = EnhancedIncidentResponseGraph()
    
    # Simulate a comprehensive incident scenario
    incident_data = {
        "incident_id": "INC-2024-002",
        "title": "Critical GraphQL Service Memory Leak",
        "description": """
        CRITICAL INCIDENT: GraphQL Service experiencing severe memory leak
        
        **Incident Details:**
        - GraphQL service memory usage spiking to 95% of allocated resources
        - UI application crashes when trying to fetch product data
        - Backend service configuration was recently changed (deployment #1234)
        - Error rates increasing rapidly across all product endpoints
        
        **Affected Services:**
        - productsGraphQLService (primary)
        - productsWebApp (secondary)
        - productsBackendService (secondary)
        
        **Impact Assessment:**
        - Customer-facing application completely unavailable
        - API response times degraded by 300%
        - Error rates at 45% and climbing
        - Business impact: High - affecting all product operations
        
        **Initial Investigation:**
        - Memory leak pattern suggests recent code changes
        - Configuration change deployed 2 hours ago
        - No similar incidents in past 30 days
        - Suspected root cause: GraphQL query optimization gone wrong
        
        **Required Actions:**
        - Immediate: Rollback recent configuration changes
        - Short-term: Implement memory monitoring and alerts
        - Long-term: Code review and optimization of GraphQL queries
        """,
        "severity": IncidentSeverity.HIGH,
        "affected_services": [
            "productsGraphQLService",
            "productsWebApp", 
            "productsBackendService"
        ],
        "github_repos": [
            "company/products-graphql-service",
            "company/products-web-app",
            "company/products-backend"
        ],
        "recent_deployment": "deployment-1234",
        "detected_at": datetime.now().isoformat()
    }
    
    print(f"📋 Incident Details:")
    print(f"   ID: {incident_data['incident_id']}")
    print(f"   Title: {incident_data['title']}")
    print(f"   Severity: {incident_data['severity']}")
    print(f"   Affected Services: {', '.join(incident_data['affected_services'])}")
    print(f"   GitHub Repos: {', '.join(incident_data['github_repos'])}")
    print()
    
    print("🔄 Starting Enhanced Incident Response Workflow...")
    print("-" * 50)
    
    try:
        # Run the enhanced incident response workflow
        final_state = await incident_graph.run_incident_response(incident_data)
        
        # Display comprehensive results
        print("\n✅ Enhanced Incident Response Completed!")
        print("=" * 70)
        
        print(f"📊 Final Status: {final_state.get('status')}")
        print(f"⏱️  Duration: {final_state.get('updated_at') - final_state.get('created_at')}")
        print(f"📝 Completed Steps: {len(final_state.get('completed_steps', []))}")
        print(f"🔍 Findings: {len(final_state.get('findings', []))}")
        print(f"💡 Recommendations: {len(final_state.get('recommendations', []))}")
        print(f"⚡ Actions Executed: {len(final_state.get('actions_taken', []))}")
        print(f"📢 Communications: {len(final_state.get('communications', []))}")
        
        # Display completed steps
        if final_state.get('completed_steps'):
            print(f"\n📋 Workflow Steps Completed:")
            for i, step in enumerate(final_state.get('completed_steps', []), 1):
                print(f"   {i}. {step}")
        
        # Display findings
        if final_state.get('findings'):
            print(f"\n🔍 Investigation Findings:")
            for i, finding in enumerate(final_state.get('findings', []), 1):
                print(f"   {i}. {finding.get('title', 'Unknown')}")
                print(f"      Severity: {finding.get('severity', 'Unknown')}")
                print(f"      Confidence: {finding.get('confidence', 0):.1%}")
                print(f"      Source: {finding.get('source', 'Unknown')}")
                print(f"      Description: {finding.get('description', 'No description')[:100]}...")
                print()
        
        # Display recommendations
        if final_state.get('recommendations'):
            print(f"\n💡 Generated Recommendations:")
            for i, recommendation in enumerate(final_state.get('recommendations', []), 1):
                print(f"   {i}. {recommendation.get('title', 'Unknown')}")
                print(f"      Priority: {recommendation.get('priority', 'Unknown')}")
                print(f"      Category: {recommendation.get('category', 'Unknown')}")
                print(f"      Effort: {recommendation.get('estimated_effort', 'Unknown')}")
                print(f"      Impact: {recommendation.get('impact', 'Unknown')}")
                print(f"      Description: {recommendation.get('description', 'No description')[:100]}...")
                print()
        
        # Display executed actions
        if final_state.get('actions_taken'):
            print(f"\n⚡ Executed Actions:")
            for i, action in enumerate(final_state.get('actions_taken', []), 1):
                print(f"   {i}. {action.get('title', 'Unknown')}")
                print(f"      Status: {action.get('status', 'Unknown')}")
                print(f"      Result: {action.get('result', 'Unknown')}")
                print()
        
        # Display Jira tickets created
        if final_state.get('jira_tickets'):
            print(f"\n📝 Jira Tickets Created:")
            for i, ticket in enumerate(final_state.get('jira_tickets', []), 1):
                print(f"   {i}. {ticket.get('key', 'Unknown')}: {ticket.get('fields', {}).get('summary', 'Unknown')}")
                print(f"      Type: {ticket.get('fields', {}).get('issuetype', {}).get('name', 'Unknown')}")
                print()
        
        # Display communications
        if final_state.get('communications'):
            print(f"\n📢 Communications Sent:")
            for i, comm in enumerate(final_state.get('communications', []), 1):
                print(f"   {i}. {comm.get('type', 'Unknown')} - {comm.get('timestamp', 'Unknown')}")
                print(f"      Message: {comm.get('message', 'No message')[:100]}...")
                print()
        
        # Display analysis results
        if final_state.get('analysis'):
            analysis = final_state.get('analysis', {})
            print(f"\n📊 Analysis Results:")
            print(f"   Root Cause: {analysis.get('root_cause', 'Unknown')}")
            print(f"   Severity Assessment: {analysis.get('severity_assessment', 'Unknown')}")
            print(f"   Immediate Actions Required: {analysis.get('immediate_actions_required', False)}")
            print(f"   Escalation Needed: {analysis.get('escalation_needed', False)}")
            print(f"   Confidence: {analysis.get('confidence', 0):.1%}")
            print(f"   Summary: {analysis.get('analysis_summary', 'No summary')}")
        
        print("\n" + "=" * 70)
        print("🎉 Enhanced Incident Response Demo Completed Successfully!")
        print("=" * 70)
        
        return final_state
        
    except Exception as e:
        print(f"❌ Error during enhanced incident response: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_mcp_integrations():
    """Test the MCP integrations independently."""
    print("\n🔧 Testing MCP Integrations...")
    print("-" * 30)
    
    try:
        from .agents.incident_response_agent import IncidentResponseAgent
        
        # Create and test the incident response agent
        agent = IncidentResponseAgent(agent_id="test-001")
        
        # Initialize integrations
        success = await agent.initialize_integrations()
        
        if success:
            print("✅ MCP integrations initialized successfully")
            
            # Test Jira integration
            if agent.jira_mcp and agent.jira_mcp.initialized:
                print("✅ Jira MCP integration working")
                
                # List available tools
                tools = await agent.jira_mcp.list_tools()
                print(f"   Available Jira tools: {len(tools)}")
                
                # Get projects
                projects = await agent.jira_mcp.get_projects()
                print(f"   Jira projects: {len(projects)}")
            
            # Test GitHub integration
            if agent.github_mcp and agent.github_mcp.initialized:
                print("✅ GitHub MCP integration working")
                print(f"   Available GitHub tools: {len(agent.github_mcp.tools)}")
            
        else:
            print("❌ MCP integrations failed to initialize")
            
    except Exception as e:
        print(f"❌ Error testing MCP integrations: {e}")


async def main():
    """Main function to run the enhanced incident response demo."""
    print("🚀 Starting Enhanced LangGraph Incident Response System")
    print("=" * 70)
    
    # Test MCP integrations first
    await test_mcp_integrations()
    
    # Run the enhanced incident response demo
    await demonstrate_enhanced_incident_response()


if __name__ == "__main__":
    asyncio.run(main())
