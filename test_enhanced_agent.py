#!/usr/bin/env python3
"""
Test script for the Enhanced LangGraph Agent with GitHub and Jira MCP Integration.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()


async def test_enhanced_agent():
    """Test the enhanced incident response agent."""
    print("🚀 Testing Enhanced LangGraph Agent")
    print("=" * 50)
    
    try:
        # Import the enhanced main module
        from src.enhanced_main import demonstrate_enhanced_incident_response, test_mcp_integrations
        
        # Test MCP integrations first
        print("\n🔧 Testing MCP Integrations...")
        await test_mcp_integrations()
        
        # Run the enhanced incident response demo
        print("\n🔄 Running Enhanced Incident Response Demo...")
        result = await demonstrate_enhanced_incident_response()
        
        if result:
            print("\n✅ Enhanced Agent Test Completed Successfully!")
            return True
        else:
            print("\n❌ Enhanced Agent Test Failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing enhanced agent: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_individual_components():
    """Test individual components of the enhanced agent."""
    print("\n🔧 Testing Individual Components...")
    print("-" * 30)
    
    try:
        # Test incident response agent
        from src.agents.incident_response_agent import IncidentResponseAgent
        
        print("📋 Testing Incident Response Agent...")
        agent = IncidentResponseAgent(agent_id="test-001")
        
        # Initialize integrations
        success = await agent.initialize_integrations()
        print(f"   MCP Integration: {'✅ Success' if success else '❌ Failed'}")
        
        if success:
            # Test investigation plan creation
            test_state = {
                'incident': {
                    'title': 'Test Incident',
                    'severity': 'HIGH',
                    'affected_services': ['test-service'],
                    'description': 'Test incident description'
                }
            }
            
            plan = await agent._create_investigation_plan(test_state)
            print(f"   Investigation Plan: {'✅ Created' if plan else '❌ Failed'}")
            
            if plan:
                print(f"      Steps: {len(plan.get('investigation_steps', []))}")
                print(f"      GitHub Repos: {len(plan.get('github_repos_to_analyze', []))}")
                print(f"      Jira Tickets: {len(plan.get('jira_tickets_needed', []))}")
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing individual components: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Enhanced LangGraph Agent Test Suite")
    print("=" * 50)
    
    # Check environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "JIRA_OAUTH_TOKEN",
        "GITHUB_PERSONAL_ACCESS_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Please set these variables in your .env file")
        return False
    
    print("✅ Environment variables configured")
    
    # Test individual components
    component_success = await test_individual_components()
    
    # Test full enhanced agent
    agent_success = await test_enhanced_agent()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Individual Components: {'✅ Passed' if component_success else '❌ Failed'}")
    print(f"   Enhanced Agent: {'✅ Passed' if agent_success else '❌ Failed'}")
    
    if component_success and agent_success:
        print("\n🎉 All Tests Passed!")
        return True
    else:
        print("\n❌ Some Tests Failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
