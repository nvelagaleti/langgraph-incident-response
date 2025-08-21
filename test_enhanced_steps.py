#!/usr/bin/env python3
"""
Test each step of the enhanced incident response workflow individually
"""

import asyncio
import sys
import os
from pathlib import Path

# Add studio directory to path
sys.path.append('studio')

async def test_step1_parse_ir_ticket():
    """Test Step 1: Parse IR ticket and generate incident details."""
    print("🧪 Testing Step 1: Parse IR Ticket")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import step1_parse_ir_ticket, IncidentState
        
        # Create initial state with only incident_id
        initial_state = IncidentState(
            incident_id='IR-2024-001'
        )
        
        print("📋 Input: incident_id = 'IR-2024-001'")
        print("🔄 Executing step1_parse_ir_ticket...")
        
        result = await step1_parse_ir_ticket(initial_state)
        
        print("✅ Step 1 completed successfully!")
        print(f"📝 Title: {result.get('title', 'N/A')}")
        print(f"📄 Description: {result.get('description', 'N/A')[:100]}...")
        print(f"🚨 Severity: {result.get('severity', 'N/A')}")
        print(f"📋 Status: {result.get('status', 'N/A')}")
        print(f"⏰ Created At: {result.get('created_at', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_setup_mcp_integrations():
    """Test MCP Integration Setup."""
    print("\n🧪 Testing MCP Integration Setup")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import setup_mcp_integrations, IncidentState
        
        # Create state with incident details
        initial_state = IncidentState(
            incident_id='IR-2024-001',
            title='Test Incident',
            description='Test description',
            severity='high',
            status='open',
            created_at=None,
            updated_at=None
        )
        
        print("🔄 Executing setup_mcp_integrations...")
        
        result = await setup_mcp_integrations(initial_state)
        
        print("✅ MCP Integration Setup completed!")
        print(f"🔗 MCP Servers: {result.get('mcp_integrations', {}).get('mcp_servers', [])}")
        print(f"🐙 GitHub Available: {result.get('mcp_integrations', {}).get('github_client_available', False)}")
        print(f"🎫 Jira Available: {result.get('mcp_integrations', {}).get('jira_client_available', False)}")
        
        return result
        
    except Exception as e:
        print(f"❌ MCP Integration Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_step2_identify_repo():
    """Test Step 2: Identify first repository."""
    print("\n🧪 Testing Step 2: Identify First Repository")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import step2_identify_first_repo, IncidentState
        
        # Create state with incident details and MCP setup
        initial_state = IncidentState(
            incident_id='IR-2024-001',
            title='UI Performance Degradation',
            description='Users reporting slow page loads and timeouts on the products page',
            severity='high',
            status='open',
            mcp_integrations={
                'github_client_available': True,
                'jira_client_available': True,
                'mcp_servers': ['GitHub', 'Jira']
            }
        )
        
        print("🔄 Executing step2_identify_first_repo...")
        
        result = await step2_identify_first_repo(initial_state)
        
        print("✅ Step 2 completed successfully!")
        print(f"🔍 First Repo: {result.get('first_repo', 'N/A')}")
        print(f"🐙 GitHub Analysis: {len(result.get('github_analysis', {}))} items")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_step3_discover_path():
    """Test Step 3: Discover repository path."""
    print("\n🧪 Testing Step 3: Discover Repository Path")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import step3_discover_repo_path, IncidentState
        
        # Create state with repo identified
        initial_state = IncidentState(
            incident_id='IR-2024-001',
            title='UI Performance Degradation',
            description='Users reporting slow page loads and timeouts on the products page',
            severity='high',
            status='open',
            first_repo='frontend-ui',
            github_analysis={
                'repositories': ['frontend-ui', 'graphql-service', 'backend-api'],
                'change_types': ['configuration', 'deployment', 'code'],
                'timeframe': 24,
                'analysis_focus': 'recent changes'
            }
        )
        
        print("🔄 Executing step3_discover_repo_path...")
        
        result = await step3_discover_repo_path(initial_state)
        
        print("✅ Step 3 completed successfully!")
        print(f"🛤️  Repo Path: {result.get('repo_path', [])}")
        print(f"📦 All Repos: {result.get('all_repos', [])}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 3 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_step4_parallel_analysis():
    """Test Step 4: Parallel analysis of commits and logs."""
    print("\n🧪 Testing Step 4: Parallel Analysis")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import step4_parallel_analysis, IncidentState
        
        # Create state with repo path discovered
        initial_state = IncidentState(
            incident_id='IR-2024-001',
            title='UI Performance Degradation',
            description='Users reporting slow page loads and timeouts on the products page',
            severity='high',
            status='open',
            first_repo='frontend-ui',
            repo_path=['frontend-ui', 'graphql-service', 'backend-api'],
            all_repos=['frontend-ui', 'graphql-service', 'backend-api']
        )
        
        print("🔄 Executing step4_parallel_analysis...")
        
        result = await step4_parallel_analysis(initial_state)
        
        print("✅ Step 4 completed successfully!")
        print(f"📝 Repo Commits: {len(result.get('repo_commits', {}))} repos")
        print(f"📊 Repo Logs: {len(result.get('repo_logs', {}))} repos")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 4 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_step5_analyze_logs():
    """Test Step 5: Analyze logs."""
    print("\n🧪 Testing Step 5: Analyze Logs")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import step5_analyze_logs, IncidentState
        
        # Create state with parallel analysis results
        initial_state = IncidentState(
            incident_id='IR-2024-001',
            title='UI Performance Degradation',
            description='Users reporting slow page loads and timeouts on the products page',
            severity='high',
            status='open',
            repo_commits={
                'frontend-ui': [{'hash': 'abc123', 'message': 'Update config', 'author': 'dev1'}],
                'graphql-service': [{'hash': 'def456', 'message': 'Fix query', 'author': 'dev2'}]
            },
            repo_logs={
                'frontend-ui': [{'level': 'ERROR', 'message': 'Timeout error', 'timestamp': '2024-01-01'}],
                'graphql-service': [{'level': 'WARN', 'message': 'Slow query', 'timestamp': '2024-01-01'}]
            }
        )
        
        print("🔄 Executing step5_analyze_logs...")
        
        result = await step5_analyze_logs(initial_state)
        
        print("✅ Step 5 completed successfully!")
        print(f"📊 Log Analysis: {len(result.get('log_analysis', {}))} items")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 5 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_step6_analyze_commits():
    """Test Step 6: Analyze commits."""
    print("\n🧪 Testing Step 6: Analyze Commits")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import step6_analyze_commits, IncidentState
        
        # Create state with log analysis
        initial_state = IncidentState(
            incident_id='IR-2024-001',
            title='UI Performance Degradation',
            description='Users reporting slow page loads and timeouts on the products page',
            severity='high',
            status='open',
            log_analysis={
                'errors': ['Timeout errors detected'],
                'warnings': ['Slow queries identified'],
                'recommendations': ['Check database performance']
            }
        )
        
        print("🔄 Executing step6_analyze_commits...")
        
        result = await step6_analyze_commits(initial_state)
        
        print("✅ Step 6 completed successfully!")
        print(f"📝 Commit Analysis: {len(result.get('commit_analysis', {}))} items")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 6 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_step7_summarize_rca():
    """Test Step 7: Summarize Root Cause Analysis."""
    print("\n🧪 Testing Step 7: Summarize RCA")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import step7_summarize_rca, IncidentState
        
        # Create state with both analyses
        initial_state = IncidentState(
            incident_id='IR-2024-001',
            title='UI Performance Degradation',
            description='Users reporting slow page loads and timeouts on the products page',
            severity='high',
            status='open',
            log_analysis={
                'errors': ['Timeout errors detected'],
                'warnings': ['Slow queries identified'],
                'recommendations': ['Check database performance']
            },
            commit_analysis={
                'suspicious_commits': ['abc123', 'def456'],
                'potential_causes': ['Configuration change', 'Query optimization'],
                'timeline': 'Last 24 hours'
            }
        )
        
        print("🔄 Executing step7_summarize_rca...")
        
        result = await step7_summarize_rca(initial_state)
        
        print("✅ Step 7 completed successfully!")
        print(f"🔍 Root Cause Analysis: {len(result.get('root_cause_analysis', {}))} items")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 7 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_step8_summarize_actions():
    """Test Step 8: Summarize Action Items."""
    print("\n🧪 Testing Step 8: Summarize Actions")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import step8_summarize_actions, IncidentState
        
        # Create state with RCA
        initial_state = IncidentState(
            incident_id='IR-2024-001',
            title='UI Performance Degradation',
            description='Users reporting slow page loads and timeouts on the products page',
            severity='high',
            status='open',
            root_cause_analysis={
                'root_cause': 'Database query performance degradation',
                'contributing_factors': ['Recent configuration change', 'Increased load'],
                'evidence': ['Timeout errors', 'Slow query logs']
            }
        )
        
        print("🔄 Executing step8_summarize_actions...")
        
        result = await step8_summarize_actions(initial_state)
        
        print("✅ Step 8 completed successfully!")
        print(f"📋 Action Items: {len(result.get('action_items', []))} items")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 8 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_create_jira_tickets():
    """Test Jira Ticket Creation."""
    print("\n🧪 Testing Jira Ticket Creation")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import create_jira_tickets, IncidentState
        
        # Create state with action items
        initial_state = IncidentState(
            incident_id='IR-2024-001',
            title='UI Performance Degradation',
            description='Users reporting slow page loads and timeouts on the products page',
            severity='high',
            status='open',
            action_items=[
                {'action': 'Optimize database queries', 'priority': 'high'},
                {'action': 'Review recent configuration changes', 'priority': 'medium'}
            ],
            github_analysis={
                'repositories': ['frontend-ui', 'graphql-service'],
                'recent_commits': [{'hash': 'abc123', 'message': 'Update config'}],
                'potential_causes': ['Configuration change']
            },
            mcp_integrations={
                'jira_client_available': True
            }
        )
        
        print("🔄 Executing create_jira_tickets...")
        
        result = await create_jira_tickets(initial_state)
        
        print("✅ Jira Ticket Creation completed!")
        print(f"🎫 Jira Tickets: {len(result.get('jira_tickets', []))} tickets")
        
        return result
        
    except Exception as e:
        print(f"❌ Jira Ticket Creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_step9_update_ticket():
    """Test Step 9: Update IR Ticket."""
    print("\n🧪 Testing Step 9: Update IR Ticket")
    print("=" * 50)
    
    try:
        from incident_response_enhanced import step9_update_ir_ticket, IncidentState
        
        # Create state with all previous steps
        initial_state = IncidentState(
            incident_id='IR-2024-001',
            title='UI Performance Degradation',
            description='Users reporting slow page loads and timeouts on the products page',
            severity='high',
            status='open',
            root_cause_analysis={
                'root_cause': 'Database query performance degradation',
                'contributing_factors': ['Recent configuration change', 'Increased load']
            },
            action_items=[
                {'action': 'Optimize database queries', 'priority': 'high'},
                {'action': 'Review recent configuration changes', 'priority': 'medium'}
            ],
            jira_tickets=[
                {'key': 'IR-1', 'summary': 'Incident: UI Performance Degradation'},
                {'key': 'IR-2', 'summary': 'Review recent commits'}
            ]
        )
        
        print("🔄 Executing step9_update_ir_ticket...")
        
        result = await step9_update_ir_ticket(initial_state)
        
        print("✅ Step 9 completed successfully!")
        print(f"📝 Updated Ticket: {result.get('updated_ticket', {}).get('status', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Step 9 failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def run_all_tests():
    """Run all step tests."""
    print("🧪 Testing Enhanced Incident Response Workflow - Step by Step")
    print("=" * 80)
    
    # Test each step
    step1_result = await test_step1_parse_ir_ticket()
    if not step1_result:
        print("❌ Stopping tests due to Step 1 failure")
        return
    
    step2_result = await test_setup_mcp_integrations()
    if not step2_result:
        print("❌ Stopping tests due to MCP setup failure")
        return
    
    step3_result = await test_step2_identify_repo()
    if not step3_result:
        print("❌ Stopping tests due to Step 2 failure")
        return
    
    step4_result = await test_step3_discover_path()
    if not step4_result:
        print("❌ Stopping tests due to Step 3 failure")
        return
    
    step5_result = await test_step4_parallel_analysis()
    if not step5_result:
        print("❌ Stopping tests due to Step 4 failure")
        return
    
    step6_result = await test_step5_analyze_logs()
    if not step6_result:
        print("❌ Stopping tests due to Step 5 failure")
        return
    
    step7_result = await test_step6_analyze_commits()
    if not step7_result:
        print("❌ Stopping tests due to Step 6 failure")
        return
    
    step8_result = await test_step7_summarize_rca()
    if not step8_result:
        print("❌ Stopping tests due to Step 7 failure")
        return
    
    step9_result = await test_step8_summarize_actions()
    if not step9_result:
        print("❌ Stopping tests due to Step 8 failure")
        return
    
    jira_result = await test_create_jira_tickets()
    if not jira_result:
        print("❌ Stopping tests due to Jira ticket creation failure")
        return
    
    final_result = await test_step9_update_ticket()
    if not final_result:
        print("❌ Stopping tests due to Step 9 failure")
        return
    
    print("\n🎉 All steps completed successfully!")
    print("✅ Enhanced incident response workflow is working correctly!")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
