"""
Main entry point for the LangGraph Incident Response System.
Demo script that simulates the OOM incident scenario.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv

from .graphs.main_graph import IncidentResponseGraph
from .types.state import IncidentSeverity, IncidentStatus


# Load environment variables
load_dotenv()


async def simulate_oom_incident():
    """
    Simulate the OOM incident scenario:
    - Backend config change triggers GraphQL memory leak
    - UI crashes due to GraphQL service failure
    - Multi-agent system investigates and resolves
    """
    
    print("🚨 Starting LangGraph Incident Response System Demo")
    print("=" * 60)
    
    # Create the incident response graph
    incident_graph = IncidentResponseGraph()
    
    # Simulate incident data
    incident_data = {
        "incident_id": "INC-2024-001",
        "title": "GraphQL Service Out of Memory Error",
        "description": """
        Critical incident affecting the products application:
        
        - GraphQL service experiencing Out of Memory (OOM) errors
        - UI application crashes when trying to fetch product data
        - Backend service configuration was recently changed
        - Memory usage spiking to 95% of allocated resources
        
        Impact:
        - Customer-facing application completely unavailable
        - API response times degraded
        - Error rates increasing rapidly
        
        Initial Assessment:
        - Severity: HIGH
        - Affected Services: productsGraphQLService, productsWebApp
        - Root Cause: Suspected memory leak triggered by backend config change
        """,
        "severity": IncidentSeverity.HIGH,
        "affected_services": [
            "productsGraphQLService",
            "productsWebApp", 
            "productsBackendService"
        ]
    }
    
    print(f"📋 Incident Details:")
    print(f"   ID: {incident_data['incident_id']}")
    print(f"   Title: {incident_data['title']}")
    print(f"   Severity: {incident_data['severity']}")
    print(f"   Affected Services: {', '.join(incident_data['affected_services'])}")
    print()
    
    print("🔄 Starting Incident Response Workflow...")
    print("-" * 40)
    
    try:
        # Run the incident response workflow
        final_state = await incident_graph.run_incident_response(incident_data)
        
        # Display results
        print("\n✅ Incident Response Completed!")
        print("=" * 60)
        
        print(f"📊 Final Status: {final_state.get('status')}")
        print(f"⏱️  Duration: {final_state.get('updated_at') - final_state.get('created_at')}")
        print(f"📝 Completed Steps: {len(final_state.get('completed_steps', []))}")
        print(f"🔍 Findings: {len(final_state.get('findings', []))}")
        print(f"💡 Recommendations: {len(final_state.get('recommendations', []))}")
        
        # Display findings
        if final_state.get('findings'):
            print("\n🔍 Key Findings:")
            for i, finding in enumerate(final_state.get('findings', []), 1):
                print(f"   {i}. {finding.get('title', 'Unknown')}")
                print(f"      Severity: {finding.get('severity', 'Unknown')}")
                print(f"      Confidence: {finding.get('confidence', 0):.1%}")
                print(f"      Description: {finding.get('description', 'No description')}")
                print()
        
        # Display recommendations
        if final_state.get('recommendations'):
            print("💡 Recommendations:")
            for i, rec in enumerate(final_state.get('recommendations', []), 1):
                print(f"   {i}. {rec.get('title', 'Unknown')}")
                print(f"      Priority: {rec.get('priority', 'Unknown')}")
                print(f"      Effort: {rec.get('estimated_effort', 'Unknown')}")
                print(f"      Actions: {', '.join(rec.get('action_items', []))}")
                print()
        
        # Display coordination results
        coordinator_assessment = final_state.get('context', {}).get('coordinator_assessment', {})
        if coordinator_assessment:
            print("🎯 Coordination Assessment:")
            situation_analysis = coordinator_assessment.get('situation_analysis', {})
            print(f"   Impact Level: {situation_analysis.get('impact_level', 'Unknown')}")
            print(f"   Urgency: {situation_analysis.get('urgency', 'Unknown')}")
            print(f"   Resource Needs: {', '.join(situation_analysis.get('resource_needs', []))}")
            print()
        
        # Display synthesis
        synthesis = final_state.get('context', {}).get('synthesis', {})
        if synthesis:
            print("📋 Incident Synthesis:")
            print(f"   Summary: {synthesis.get('summary', 'No summary available')}")
            print()
        
        # Display finalization
        finalization = final_state.get('context', {}).get('finalization', {})
        if finalization:
            print("🏁 Final Summary:")
            print(f"   Summary: {finalization.get('summary', 'No summary available')}")
            print()
        
        print("🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during incident response: {e}")
        raise


async def demo_memory_capabilities():
    """Demo the memory capabilities of the system."""
    
    print("\n🧠 Memory Capabilities Demo")
    print("=" * 40)
    
    # Create a simple incident for memory demo
    incident_data = {
        "incident_id": "MEM-2024-001",
        "title": "Memory System Test",
        "description": "Testing memory capabilities of the incident response system",
        "severity": IncidentSeverity.MEDIUM,
        "affected_services": ["test-service"]
    }
    
    incident_graph = IncidentResponseGraph()
    
    # Run a quick incident response
    state = await incident_graph.run_incident_response(incident_data)
    
    # Display memory information
    memories = state.get('memories', {})
    if memories and memories.get('memories'):
        print(f"📚 Total Memories: {len(memories.get('memories', []))}")
        print("Recent Memories:")
        for i, memory in enumerate(memories.get('memories', [])[-3:], 1):
            print(f"   {i}. {memory.get('content', 'No content')[:100]}...")
            print(f"      Source: {memory.get('source', 'Unknown')}")
            print(f"      Tags: {', '.join(memory.get('tags', []))}")
            print()
    
    print("✅ Memory demo completed!")


async def demo_parallel_execution():
    """Demo the parallel execution capabilities."""
    
    print("\n⚡ Parallel Execution Demo")
    print("=" * 40)
    
    # Create incident data
    incident_data = {
        "incident_id": "PAR-2024-001",
        "title": "Parallel Execution Test",
        "description": "Testing parallel execution of investigation, analysis, and communication",
        "severity": IncidentSeverity.HIGH,
        "affected_services": ["service-a", "service-b", "service-c"]
    }
    
    incident_graph = IncidentResponseGraph()
    
    print("🔄 Running parallel subgraphs...")
    start_time = datetime.now()
    
    # Run the incident response
    state = await incident_graph.run_incident_response(incident_data)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"⏱️  Total Duration: {duration}")
    print(f"📊 Completed Steps: {state.get('completed_steps', [])}")
    
    # Show parallel execution results
    context = state.get('context', {})
    
    if 'investigation_results' in context:
        print("🔍 Investigation completed in parallel")
    
    if 'analysis_results' in context:
        print("📈 Analysis completed in parallel")
    
    if 'communication_results' in context:
        print("📢 Communication completed in parallel")
    
    if 'execution_results' in context:
        print("⚙️  Execution completed in parallel")
    
    print("✅ Parallel execution demo completed!")


async def main():
    """Main demo function."""
    
    print("🚀 LangGraph Incident Response System")
    print("Enhanced with Module 4 & 5 Concepts + Real MCP Integration")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Using mock responses.")
    
    # Check MCP environment
    mcp_available = False
    if os.getenv("GITHUB_TOKEN") and os.getenv("JIRA_TOKEN"):
        mcp_available = True
        print("✅ MCP credentials found - will use real GitHub and Jira data")
    else:
        print("⚠️  MCP credentials not found - using simulated data")
        print("   Set GITHUB_TOKEN, JIRA_URL, JIRA_TOKEN for real integration")
    
    # Run demos
    await simulate_oom_incident()
    await demo_memory_capabilities()
    await demo_parallel_execution()
    
    print("\n🎯 All demos completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Multi-agent architecture with specialized roles")
    print("✅ Parallel execution using subgraphs")
    print("✅ Memory management and persistence")
    print("✅ State management and checkpointing")
    print("✅ Coordinated workflow management")
    print("✅ Root cause analysis automation")
    print("✅ Incident response automation")
    if mcp_available:
        print("✅ Real MCP integration with GitHub and Jira")
    else:
        print("⚠️  Simulated MCP integration (set credentials for real data)")


if __name__ == "__main__":
    asyncio.run(main())
