#!/usr/bin/env python3
"""
Test script to run each step of the incident response workflow individually.
This allows us to debug and verify each step before running the full workflow.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the enhanced incident response module
from incident_response_enhanced import (
    step1_parse_ir_ticket,
    step2_identify_first_repo,
    step3_discover_repo_path,
    step4_parallel_analysis,
    step5_analyze_logs,
    step6_analyze_commits,
    step7_summarize_rca,
    step8_summarize_actions,
    step9_update_ir_ticket,
    setup_mcp_integrations,
    create_jira_tickets,
    IncidentInput,
    IncidentState
)

# Test incident ID
TEST_INCIDENT_ID = "IR-001"

async def test_step1_parse_ir_ticket():
    """Test Step 1: Parse IR ticket and fetch from Jira MCP"""
    print("\n" + "="*60)
    print("🧪 TESTING STEP 1: Parse IR Ticket")
    print("="*60)
    
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
        print(f"📚 GitHub Analysis Repos: {result.get('github_analysis', {}).get('repositories_to_check', [])}")
        print(f"✅ Completed Steps: {result.get('completed_steps', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 1 failed: {e}")
        return None

async def test_step2_identify_first_repo(state: IncidentState):
    """Test Step 2: Identify first repository"""
    print("\n" + "="*60)
    print("🧪 TESTING STEP 2: Identify First Repository")
    print("="*60)
    
    try:
        # Run step 2
        result = await step2_identify_first_repo(state)
        
        print(f"✅ Step 2 completed successfully!")
        print(f"🎯 First Repository: {result.get('first_repo', 'N/A')}")
        print(f"📚 All Repositories: {result.get('all_repos', [])}")
        print(f"✅ Completed Steps: {result.get('completed_steps', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 2 failed: {e}")
        return None

async def test_step3_discover_repo_path(state: IncidentState):
    """Test Step 3: Discover repository path"""
    print("\n" + "="*60)
    print("🧪 TESTING STEP 3: Discover Repository Path")
    print("="*60)
    
    try:
        # Run step 3
        result = await step3_discover_repo_path(state)
        
        print(f"✅ Step 3 completed successfully!")
        print(f"🛣️  Repository Path: {result.get('repo_path', [])}")
        print(f"✅ Completed Steps: {result.get('completed_steps', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 3 failed: {e}")
        return None

async def test_step4_parallel_analysis(state: IncidentState):
    """Test Step 4: Parallel analysis of commits and logs"""
    print("\n" + "="*60)
    print("🧪 TESTING STEP 4: Parallel Analysis")
    print("="*60)
    
    try:
        # Run step 4
        result = await step4_parallel_analysis(state)
        
        print(f"✅ Step 4 completed successfully!")
        print(f"📝 Repo Commits: {len(result.get('repo_commits', {}))} repos")
        print(f"📊 Repo Logs: {len(result.get('repo_logs', {}))} repos")
        print(f"✅ Completed Steps: {result.get('completed_steps', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 4 failed: {e}")
        return None

async def test_step5_analyze_logs(state: IncidentState):
    """Test Step 5: Analyze logs"""
    print("\n" + "="*60)
    print("🧪 TESTING STEP 5: Analyze Logs")
    print("="*60)
    
    try:
        # Run step 5
        result = await step5_analyze_logs(state)
        
        print(f"✅ Step 5 completed successfully!")
        print(f"📊 Log Analysis: {result.get('log_analysis', {})}")
        print(f"✅ Completed Steps: {result.get('completed_steps', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 5 failed: {e}")
        return None

async def test_step6_analyze_commits(state: IncidentState):
    """Test Step 6: Analyze commits"""
    print("\n" + "="*60)
    print("🧪 TESTING STEP 6: Analyze Commits")
    print("="*60)
    
    try:
        # Run step 6
        result = await step6_analyze_commits(state)
        
        print(f"✅ Step 6 completed successfully!")
        print(f"📝 Commit Analysis: {result.get('commit_analysis', {})}")
        print(f"✅ Completed Steps: {result.get('completed_steps', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 6 failed: {e}")
        return None

async def test_step7_summarize_rca(state: IncidentState):
    """Test Step 7: Summarize RCA"""
    print("\n" + "="*60)
    print("🧪 TESTING STEP 7: Summarize RCA")
    print("="*60)
    
    try:
        # Run step 7
        result = await step7_summarize_rca(state)
        
        print(f"✅ Step 7 completed successfully!")
        print(f"🔍 Root Cause Analysis: {result.get('root_cause_analysis', {})}")
        print(f"✅ Completed Steps: {result.get('completed_steps', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 7 failed: {e}")
        return None

async def test_step8_summarize_actions(state: IncidentState):
    """Test Step 8: Summarize action items"""
    print("\n" + "="*60)
    print("🧪 TESTING STEP 8: Summarize Actions")
    print("="*60)
    
    try:
        # Run step 8
        result = await step8_summarize_actions(state)
        
        print(f"✅ Step 8 completed successfully!")
        print(f"📋 Action Items: {len(result.get('action_items', []))} items")
        print(f"✅ Completed Steps: {result.get('completed_steps', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 8 failed: {e}")
        return None

async def test_step9_update_ir_ticket(state: IncidentState):
    """Test Step 9: Update IR ticket"""
    print("\n" + "="*60)
    print("🧪 TESTING STEP 9: Update IR Ticket")
    print("="*60)
    
    try:
        # Run step 9
        result = await step9_update_ir_ticket(state)
        
        print(f"✅ Step 9 completed successfully!")
        print(f"📝 Updated Ticket: {result.get('updated_ticket', {})}")
        print(f"✅ Completed Steps: {result.get('completed_steps', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 9 failed: {e}")
        return None

async def test_mcp_integrations():
    """Test MCP integrations setup"""
    print("\n" + "="*60)
    print("🧪 TESTING MCP INTEGRATIONS")
    print("="*60)
    
    try:
        # Run MCP setup
        result = await setup_mcp_integrations({})
        
        print(f"✅ MCP Integrations setup completed!")
        print(f"🔗 GitHub Enabled: {result.get('mcp_integrations', {}).get('github_enabled', False)}")
        print(f"🔗 Jira Enabled: {result.get('mcp_integrations', {}).get('jira_enabled', False)}")
        
        return result
        
    except Exception as e:
        print(f"❌ MCP Integrations failed: {e}")
        return None

async def test_create_jira_tickets(state: IncidentState):
    """Test Jira ticket creation"""
    print("\n" + "="*60)
    print("🧪 TESTING JIRA TICKET CREATION")
    print("="*60)
    
    try:
        # Run Jira ticket creation
        result = await create_jira_tickets(state)
        
        print(f"✅ Jira ticket creation completed!")
        print(f"📝 Created Tickets: {len(result.get('jira_tickets', []))} tickets")
        
        return result
        
    except Exception as e:
        print(f"❌ Jira ticket creation failed: {e}")
        return None

async def run_all_tests():
    """Run all tests in sequence"""
    print("🚀 Starting Step-by-Step Testing of Incident Response Workflow")
    print("="*80)
    
    # Test MCP integrations first
    mcp_result = await test_mcp_integrations()
    if not mcp_result:
        print("❌ MCP integrations failed, stopping tests")
        return
    
    # Test each step in sequence
    step1_result = await test_step1_parse_ir_ticket()
    if not step1_result:
        print("❌ Step 1 failed, stopping tests")
        return
    
    step2_result = await test_step2_identify_first_repo(step1_result)
    if not step2_result:
        print("❌ Step 2 failed, stopping tests")
        return
    
    step3_result = await test_step3_discover_repo_path(step2_result)
    if not step3_result:
        print("❌ Step 3 failed, stopping tests")
        return
    
    step4_result = await test_step4_parallel_analysis(step3_result)
    if not step4_result:
        print("❌ Step 4 failed, stopping tests")
        return
    
    step5_result = await test_step5_analyze_logs(step4_result)
    if not step5_result:
        print("❌ Step 5 failed, stopping tests")
        return
    
    step6_result = await test_step6_analyze_commits(step5_result)
    if not step6_result:
        print("❌ Step 6 failed, stopping tests")
        return
    
    step7_result = await test_step7_summarize_rca(step6_result)
    if not step7_result:
        print("❌ Step 7 failed, stopping tests")
        return
    
    step8_result = await test_step8_summarize_actions(step7_result)
    if not step8_result:
        print("❌ Step 8 failed, stopping tests")
        return
    
    step9_result = await test_step9_update_ir_ticket(step8_result)
    if not step9_result:
        print("❌ Step 9 failed, stopping tests")
        return
    
    # Test Jira ticket creation
    jira_result = await test_create_jira_tickets(step9_result)
    
    print("\n" + "="*80)
    print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"✅ All 9 steps completed for incident: {TEST_INCIDENT_ID}")
    print(f"📊 Final state keys: {list(step9_result.keys())}")
    print(f"📝 Total messages: {len(step9_result.get('messages', []))}")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_all_tests())
