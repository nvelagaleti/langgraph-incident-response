#!/usr/bin/env python3
"""
Test script to run the enhanced incident response workflow.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the studio directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'studio'))

from studio.incident_response_enhanced import graph


async def run_enhanced_workflow():
    """Run the enhanced incident response workflow with test data."""
    
    print("🚀 Starting Enhanced Incident Response Workflow")
    print("=" * 60)
    
    # Test IR ticket data
    test_ir_ticket = {
        "incident_id": "IR-1",
        "title": "Products page not loading - UI error",
        "description": "Users cannot access the Products page. UI shows error message 'Could not connect to GraphQL service'. API calls are failing with timeout errors. Backend service configuration was recently changed.",
        "severity": "HIGH",
        "affected_components": ["UI", "GraphQL", "Backend"],
        "user_impact": "Users cannot view or purchase products",
        "reported_by": "Customer Support",
        "created_at": datetime.now().isoformat()
    }
    
    # Initial state
    initial_state = {
        "ir_ticket": test_ir_ticket,
        "title": "Products page not loading - UI error",
        "description": "Users cannot access the Products page. UI shows error message 'Could not connect to GraphQL service'. API calls are failing with timeout errors. Backend service configuration was recently changed.",
        "severity": "HIGH",
        "messages": []
    }
    
    print(f"📋 IR Ticket: {test_ir_ticket['title']}")
    print(f"🔴 Severity: {test_ir_ticket['severity']}")
    print(f"📄 Description: {test_ir_ticket['description'][:100]}...")
    print()
    
    try:
        # Run the workflow
        print("🔄 Executing workflow...")
        result = await graph.ainvoke(initial_state)
        
        print("\n" + "=" * 60)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        # Display results
        print(f"📊 Final Status: {result.get('status', 'Unknown')}")
        print(f"🔢 Completed Steps: {len(result.get('completed_steps', []))}")
        
        if 'completed_steps' in result:
            print("\n📋 Completed Steps:")
            for i, step in enumerate(result['completed_steps'], 1):
                print(f"   {i}. {step}")
        
        if 'first_repo' in result:
            print(f"\n🎯 First Repository Identified: {result['first_repo']}")
        
        if 'repo_path' in result:
            print(f"🛤️  Repository Path: {' → '.join(result['repo_path'])}")
        
        if 'root_cause_analysis' in result:
            rca = result['root_cause_analysis']
            print(f"\n🎯 Root Cause: {rca.get('root_cause', 'Not determined')}")
            confidence = rca.get('confidence', 0)
            print(f"📊 Confidence: {confidence:.1%}")
        
        if 'action_items' in result:
            print(f"\n📋 Action Items: {len(result['action_items'])} identified")
            for i, action in enumerate(result['action_items'][:3], 1):  # Show first 3
                print(f"   {i}. [{action.get('priority', 'unknown').upper()}] {action.get('action', 'Unknown action')}")
        
        if 'updated_ticket' in result:
            print(f"\n📝 Ticket Status: {result['updated_ticket'].get('status', 'Unknown')}")
        
        print(f"\n💬 Total Messages: {len(result.get('messages', []))}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Workflow failed with error: {e}")
        print("\n💡 This might be due to:")
        print("   - Missing OpenAI API key")
        print("   - Network connectivity issues")
        print("   - Configuration problems")
        return None


def run_sync():
    """Synchronous wrapper for the async workflow."""
    return asyncio.run(run_enhanced_workflow())


if __name__ == "__main__":
    print("🎯 Enhanced Incident Response Workflow Test")
    print("This script demonstrates the 9-step automated incident investigation process.")
    print()
    
    result = run_sync()
    
    if result:
        print("\n🎉 Test completed successfully!")
        print("\n📈 Next Steps:")
        print("   1. Review the generated RCA and action items")
        print("   2. Implement the recommended actions")
        print("   3. Update monitoring and alerting")
        print("   4. Document lessons learned")
    else:
        print("\n⚠️  Test completed with issues.")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your .env file for required API keys")
        print("   2. Verify network connectivity")
        print("   3. Review the error messages above")
