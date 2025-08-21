#!/usr/bin/env python3
"""
Test script to verify the LangGraph Studio setup.
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the studio directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'studio'))

# Load environment variables
load_dotenv()


async def test_basic_incident_response():
    """Test the basic incident response graph."""
    print("🧪 Testing Basic Incident Response Graph...")
    
    try:
        from studio.incident_response_basic import graph
        
        # Create test incident
        initial_state = {
            "title": "Test Service Outage",
            "description": "API service is experiencing intermittent failures",
            "severity": "MEDIUM",
            "messages": []
        }
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        print(f"✅ Basic incident response completed")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Findings: {len(result.get('findings', []))}")
        print(f"   Recommendations: {len(result.get('recommendations', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic incident response test failed: {e}")
        return False


async def test_coordinator_agent():
    """Test the coordinator agent graph."""
    print("🧪 Testing Coordinator Agent Graph...")
    
    try:
        from studio.coordinator_agent import graph
        
        # Create test incident
        initial_state = {
            "title": "Critical Database Issue",
            "description": "Database connection pool exhausted",
            "severity": "HIGH",
            "messages": []
        }
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        print(f"✅ Coordinator agent completed")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Assigned Agents: {len(result.get('assigned_agents', []))}")
        print(f"   Next Steps: {len(result.get('next_steps', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Coordinator agent test failed: {e}")
        return False


async def test_investigator_agent():
    """Test the investigator agent graph."""
    print("🧪 Testing Investigator Agent Graph...")
    
    try:
        from studio.investigator_agent import graph
        
        # Create test incident
        initial_state = {
            "title": "Memory Leak Investigation",
            "description": "Application memory usage increasing over time",
            "severity": "HIGH",
            "messages": []
        }
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        print(f"✅ Investigator agent completed")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Findings: {len(result.get('findings', []))}")
        print(f"   Root Cause: {result.get('root_cause_analysis', {}).get('root_cause', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Investigator agent test failed: {e}")
        return False


async def test_enhanced_incident_response():
    """Test the enhanced incident response graph."""
    print("🧪 Testing Enhanced Incident Response Graph...")
    
    try:
        from studio.incident_response_enhanced import graph
        
        # Create test incident
        initial_state = {
            "title": "Multi-Service Failure",
            "description": "Multiple services failing due to network issues",
            "severity": "CRITICAL",
            "messages": []
        }
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        print(f"✅ Enhanced incident response completed")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Completed Steps: {len(result.get('completed_steps', []))}")
        print(f"   Communications: {len(result.get('communications', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced incident response test failed: {e}")
        return False


async def test_mcp_integration():
    """Test the MCP integration graph."""
    print("🧪 Testing MCP Integration Graph...")
    
    try:
        from studio.incident_response_with_mcp import graph
        
        # Create test incident
        initial_state = {
            "title": "Deployment Failure",
            "description": "Recent deployment caused service degradation",
            "severity": "HIGH",
            "messages": []
        }
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        print(f"✅ MCP integration completed")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   MCP Servers: {result.get('mcp_integrations', {}).get('mcp_servers', [])}")
        print(f"   GitHub Analysis: {bool(result.get('github_analysis', {}))}")
        print(f"   Jira Tickets: {len(result.get('jira_tickets', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
        return False


async def test_configuration():
    """Test the configuration system."""
    print("🧪 Testing Configuration System...")
    
    try:
        from studio.configuration import Configuration
        
        # Test configuration creation
        config = Configuration(
            user_id="test-user",
            incident_severity="HIGH",
            enable_mcp_integration=True
        )
        
        print(f"✅ Configuration test completed")
        print(f"   User ID: {config.user_id}")
        print(f"   Incident Severity: {config.incident_severity}")
        print(f"   MCP Integration: {config.enable_mcp_integration}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 LangGraph Studio Setup Test Suite")
    print("=" * 50)
    
    # Check environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Some tests may fail without proper configuration")
    
    # Run tests
    tests = [
        ("Configuration", test_configuration),
        ("Basic Incident Response", test_basic_incident_response),
        ("Coordinator Agent", test_coordinator_agent),
        ("Investigator Agent", test_investigator_agent),
        ("Enhanced Incident Response", test_enhanced_incident_response),
        ("MCP Integration", test_mcp_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Studio setup is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Check configuration and dependencies.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
