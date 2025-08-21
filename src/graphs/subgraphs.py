"""
Subgraphs for the LangGraph Incident Response System.
Following patterns from Module 4 Sub-graphs.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from ..types.state import (
    InvestigationState,
    AnalysisState,
    CommunicationState,
    ExecutionState,
    InvestigationFinding,
    Recommendation,
    IncidentSeverity
)
from ..agents.base_agent import BaseAgent, AgentFactory


def create_investigation_subgraph():
    """
    Create investigation subgraph for root cause analysis.
    Following patterns from Module 4 Sub-graphs.
    """
    
    builder = StateGraph(InvestigationState)
    
    # Add nodes
    builder.add_node("start_investigation", _start_investigation)
    builder.add_node("analyze_logs", _analyze_logs)
    builder.add_node("analyze_git_commits", _analyze_git_commits)
    builder.add_node("correlate_evidence", _correlate_evidence)
    builder.add_node("generate_findings", _generate_findings)
    builder.add_node("complete_investigation", _complete_investigation)
    
    # Add edges
    builder.add_edge(START, "start_investigation")
    builder.add_edge("start_investigation", "analyze_logs")
    builder.add_edge("start_investigation", "analyze_git_commits")
    builder.add_edge("analyze_logs", "correlate_evidence")
    builder.add_edge("analyze_git_commits", "correlate_evidence")
    builder.add_edge("correlate_evidence", "generate_findings")
    builder.add_edge("generate_findings", "complete_investigation")
    builder.add_edge("complete_investigation", END)
    
    return builder.compile(checkpointer=MemorySaver())


def create_analysis_subgraph():
    """
    Create analysis subgraph for data analysis and pattern recognition.
    Following patterns from Module 4 Sub-graphs.
    """
    
    builder = StateGraph(AnalysisState)
    
    # Add nodes
    builder.add_node("start_analysis", _start_analysis)
    builder.add_node("analyze_performance", _analyze_performance)
    builder.add_node("analyze_patterns", _analyze_patterns)
    builder.add_node("identify_correlations", _identify_correlations)
    builder.add_node("generate_insights", _generate_insights)
    builder.add_node("complete_analysis", _complete_analysis)
    
    # Add edges
    builder.add_edge(START, "start_analysis")
    builder.add_edge("start_analysis", "analyze_performance")
    builder.add_edge("start_analysis", "analyze_patterns")
    builder.add_edge("analyze_performance", "identify_correlations")
    builder.add_edge("analyze_patterns", "identify_correlations")
    builder.add_edge("identify_correlations", "generate_insights")
    builder.add_edge("generate_insights", "complete_analysis")
    builder.add_edge("complete_analysis", END)
    
    return builder.compile(checkpointer=MemorySaver())


def create_communication_subgraph():
    """
    Create communication subgraph for stakeholder communication.
    Following patterns from Module 4 Sub-graphs.
    """
    
    builder = StateGraph(CommunicationState)
    
    # Add nodes
    builder.add_node("start_communication", _start_communication)
    builder.add_node("identify_stakeholders", _identify_stakeholders)
    builder.add_node("create_communication_plan", _create_communication_plan)
    builder.add_node("send_initial_notifications", _send_initial_notifications)
    builder.add_node("monitor_responses", _monitor_responses)
    builder.add_node("escalate_if_needed", _escalate_if_needed)
    builder.add_node("complete_communication", _complete_communication)
    
    # Add edges
    builder.add_edge(START, "start_communication")
    builder.add_edge("start_communication", "identify_stakeholders")
    builder.add_edge("identify_stakeholders", "create_communication_plan")
    builder.add_edge("create_communication_plan", "send_initial_notifications")
    builder.add_edge("send_initial_notifications", "monitor_responses")
    builder.add_edge("monitor_responses", "escalate_if_needed")
    builder.add_edge("escalate_if_needed", "complete_communication")
    builder.add_edge("complete_communication", END)
    
    return builder.compile(checkpointer=MemorySaver())


def create_execution_subgraph():
    """
    Create execution subgraph for action implementation.
    Following patterns from Module 4 Sub-graphs.
    """
    
    builder = StateGraph(ExecutionState)
    
    # Add nodes
    builder.add_node("start_execution", _start_execution)
    builder.add_node("plan_actions", _plan_actions)
    builder.add_node("allocate_resources", _allocate_resources)
    builder.add_node("execute_actions", _execute_actions)
    builder.add_node("monitor_progress", _monitor_progress)
    builder.add_node("handle_failures", _handle_failures)
    builder.add_node("complete_execution", _complete_execution)
    
    # Add edges
    builder.add_edge(START, "start_execution")
    builder.add_edge("start_execution", "plan_actions")
    builder.add_edge("plan_actions", "allocate_resources")
    builder.add_edge("allocate_resources", "execute_actions")
    builder.add_edge("execute_actions", "monitor_progress")
    builder.add_edge("monitor_progress", "handle_failures")
    builder.add_edge("handle_failures", "complete_execution")
    builder.add_edge("complete_execution", END)
    
    return builder.compile(checkpointer=MemorySaver())


# Investigation subgraph functions
async def _start_investigation(state: InvestigationState) -> InvestigationState:
    """Start the investigation process."""
    state.update({
        "status": "investigating",
        "analysis_notes": state.get("analysis_notes", []) + ["Investigation started"]
    })
    return state


async def _analyze_logs(state: InvestigationState) -> InvestigationState:
    """Analyze service logs for evidence."""
    # Simulate log analysis
    log_evidence = [
        {
            "source": "GraphQL Service",
            "timestamp": datetime.now(),
            "level": "ERROR",
            "message": "Memory usage exceeded threshold",
            "details": "Memory usage: 95% of allocated 512MB"
        },
        {
            "source": "Backend Service", 
            "timestamp": datetime.now(),
            "level": "INFO",
            "message": "Configuration updated",
            "details": "Processing timeout increased to 30 seconds"
        }
    ]
    
    state.update({
        "evidence": state.get("evidence", []) + log_evidence,
        "analysis_notes": state.get("analysis_notes", []) + ["Log analysis completed"]
    })
    return state


    async def _analyze_git_commits(state: InvestigationState) -> InvestigationState:
        """Analyze git commits for changes using MCP."""
        from ..services.langchain_mcp_client import langchain_mcp_client
        import os
        
        # Get commits from the last 24 hours
        from datetime import timedelta
        until_date = datetime.now()
        since_date = until_date - timedelta(days=1)
        
        # Check for multiple repositories
        github_repos = os.getenv("GITHUB_REPOSITORIES")
        
        if github_repos:
            # Multi-repo analysis
            repositories = []
            for repo in github_repos.split(","):
                owner, name = repo.strip().split("/")
                repositories.append({"owner": owner, "name": name})
            
            # Get commits from all repositories
            commits = await langchain_mcp_client.get_github_commits_multi_repo(
                since_date=since_date.isoformat(),
                until_date=until_date.isoformat(),
                repositories=repositories
            )
        else:
            # Single repo analysis (legacy)
            github_owner = os.getenv("GITHUB_OWNER")
            github_repo = os.getenv("GITHUB_REPO")
            
            commits = await langchain_mcp_client.get_github_commits(
                since_date=since_date.isoformat(),
                until_date=until_date.isoformat(),
                repo_owner=github_owner,
                repo_name=github_repo
            )
        
        commit_evidence = []
        for commit in commits:
            # Get detailed file changes for each commit
            file_changes = await langchain_mcp_client.get_github_file_changes(commit.sha)
            
            commit_evidence.append({
                "repository": commit.repository,
                "commit_sha": commit.sha,
                "author": commit.author,
                "message": commit.message,
                "files_changed": [f["filename"] for f in file_changes],
                "file_changes": file_changes,
                "timestamp": commit.date
            })
        
        state.update({
            "evidence": state.get("evidence", []) + commit_evidence,
            "analysis_notes": state.get("analysis_notes", []) + [f"Git commit analysis completed - found {len(commits)} commits across repositories"]
        })
        return state


async def _correlate_evidence(state: InvestigationState) -> InvestigationState:
    """Correlate evidence to identify patterns."""
    evidence = state.get("evidence", [])
    
    # Simple correlation logic
    memory_issues = [e for e in evidence if "memory" in str(e).lower()]
    config_changes = [e for e in evidence if "config" in str(e).lower()]
    
    correlation_notes = [
        f"Found {len(memory_issues)} memory-related issues",
        f"Found {len(config_changes)} configuration changes",
        "Correlating memory issues with recent config changes"
    ]
    
    state.update({
        "analysis_notes": state.get("analysis_notes", []) + correlation_notes,
        "confidence_level": 0.8 if memory_issues and config_changes else 0.3
    })
    return state


async def _generate_findings(state: InvestigationState) -> InvestigationState:
    """Generate investigation findings."""
    evidence = state.get("evidence", [])
    
    # Generate findings based on evidence
    findings = []
    
    memory_evidence = [e for e in evidence if "memory" in str(e).lower()]
    if memory_evidence:
        findings.append(InvestigationFinding(
            finding_id=f"finding-{uuid.uuid4().hex[:8]}",
            title="Memory Leak Detected in GraphQL Service",
            description="GraphQL service experiencing memory usage spikes",
            severity=IncidentSeverity.HIGH,
            evidence=[str(e) for e in memory_evidence],
            confidence=0.9,
            agent_id=state.get("investigator_id"),
            timestamp=datetime.now()
        ))
    
    config_evidence = [e for e in evidence if "config" in str(e).lower()]
    if config_evidence:
        findings.append(InvestigationFinding(
            finding_id=f"finding-{uuid.uuid4().hex[:8]}",
            title="Recent Configuration Changes",
            description="Backend service configuration modified recently",
            severity=IncidentSeverity.MEDIUM,
            evidence=[str(e) for e in config_evidence],
            confidence=0.8,
            agent_id=state.get("investigator_id"),
            timestamp=datetime.now()
        ))
    
    state.update({
        "findings": state.get("findings", []) + findings,
        "analysis_notes": state.get("analysis_notes", []) + ["Findings generated"]
    })
    return state


async def _complete_investigation(state: InvestigationState) -> InvestigationState:
    """Complete the investigation."""
    state.update({
        "status": "completed",
        "analysis_notes": state.get("analysis_notes", []) + ["Investigation completed"]
    })
    return state


# Analysis subgraph functions
async def _start_analysis(state: AnalysisState) -> AnalysisState:
    """Start the analysis process."""
    state.update({
        "status": "analyzing"
    })
    return state


async def _analyze_performance(state: AnalysisState) -> AnalysisState:
    """Analyze performance metrics."""
    # Simulate performance analysis
    performance_results = [
        {
            "metric": "response_time",
            "value": 2.5,
            "threshold": 1.0,
            "status": "degraded"
        },
        {
            "metric": "memory_usage",
            "value": 95,
            "threshold": 80,
            "status": "critical"
        }
    ]
    
    state.update({
        "analysis_results": state.get("analysis_results", []) + performance_results
    })
    return state


async def _analyze_patterns(state: AnalysisState) -> AnalysisState:
    """Analyze patterns in the data."""
    # Simulate pattern analysis
    patterns = [
        {
            "pattern_type": "memory_growth",
            "description": "Steady increase in memory usage over time",
            "confidence": 0.85
        },
        {
            "pattern_type": "error_spike",
            "description": "Sudden increase in error rates",
            "confidence": 0.9
        }
    ]
    
    state.update({
        "patterns": state.get("patterns", []) + patterns
    })
    return state


async def _identify_correlations(state: AnalysisState) -> AnalysisState:
    """Identify correlations between different metrics."""
    # Simulate correlation analysis
    correlations = [
        {
            "factor_a": "memory_usage",
            "factor_b": "response_time",
            "correlation": 0.75,
            "description": "High correlation between memory usage and response time"
        }
    ]
    
    state.update({
        "correlations": state.get("correlations", []) + correlations
    })
    return state


async def _generate_insights(state: AnalysisState) -> AnalysisState:
    """Generate insights from analysis."""
    patterns = state.get("patterns", [])
    correlations = state.get("correlations", [])
    
    insights = []
    
    if patterns:
        insights.append("Memory growth pattern indicates potential memory leak")
    
    if correlations:
        insights.append("Memory usage directly impacts response time")
    
    insights.append("Immediate action required to prevent service degradation")
    
    state.update({
        "insights": state.get("insights", []) + insights
    })
    return state


async def _complete_analysis(state: AnalysisState) -> AnalysisState:
    """Complete the analysis."""
    state.update({
        "status": "completed"
    })
    return state


# Communication subgraph functions
async def _start_communication(state: CommunicationState) -> CommunicationState:
    """Start the communication process."""
    state.update({
        "status": "communicating"
    })
    return state


async def _identify_stakeholders(state: CommunicationState) -> CommunicationState:
    """Identify stakeholders for communication."""
    # Simulate stakeholder identification
    stakeholders = ["engineering_team", "management", "customers", "oncall_engineer"]
    
    state.update({
        "stakeholders": stakeholders
    })
    return state


async def _create_communication_plan(state: CommunicationState) -> CommunicationState:
    """Create communication plan."""
    plan = {
        "immediate": ["oncall_engineer", "engineering_team"],
        "within_1_hour": ["management"],
        "within_4_hours": ["customers"],
        "escalation_triggers": ["no_response_30min", "severity_increase"]
    }
    
    state.update({
        "communication_plan": plan
    })
    return state


async def _send_initial_notifications(state: CommunicationState) -> CommunicationState:
    """Send initial notifications using MCP."""
    from ..services.langchain_mcp_client import langchain_mcp_client
    
    messages = []
    
    # Create Jira ticket for incident notification
    if langchain_mcp_client.initialized:
        try:
            incident_summary = f"Critical Incident Alert - {state.get('incident_id')}"
            incident_description = f"""
            **CRITICAL INCIDENT DETECTED**
            
            Incident ID: {state.get('incident_id')}
            Severity: HIGH
            Status: INVESTIGATING
            
            **Immediate Action Required:**
            - On-call engineer needs to acknowledge
            - Engineering team should be notified
            - Stakeholders need to be updated
            
            **Next Steps:**
            1. Acknowledge this incident
            2. Begin investigation
            3. Update status as progress is made
            """
            
            issue_key = await langchain_mcp_client.create_jira_issue(
                summary=incident_summary,
                description=incident_description,
                issue_type="Incident"
            )
            
            if issue_key:
                messages.append({
                    "recipient": "jira_system",
                    "message": f"Critical incident ticket created: {issue_key}",
                    "timestamp": datetime.now(),
                    "status": "sent",
                    "ticket_key": issue_key
                })
                
                # Add comment for on-call engineer
                await langchain_mcp_client.add_jira_comment(
                    issue_key=issue_key,
                    comment="**ON-CALL ENGINEER ALERT**\n\nCritical incident detected - immediate attention required.\n\nPlease acknowledge and begin investigation."
                )
                
        except Exception as e:
            print(f"❌ Error creating Jira notification: {e}")
    
    # Fallback to simulated messages if MCP not available
    if not messages:
        messages = [
            {
                "recipient": "oncall_engineer",
                "message": "Critical incident detected - immediate attention required",
                "timestamp": datetime.now(),
                "status": "sent"
            },
            {
                "recipient": "engineering_team",
                "message": "Incident investigation in progress",
                "timestamp": datetime.now(),
                "status": "sent"
            }
        ]
    
    state.update({
        "messages_sent": state.get("messages_sent", []) + messages
    })
    return state


async def _monitor_responses(state: CommunicationState) -> CommunicationState:
    """Monitor stakeholder responses."""
    # Simulate response monitoring
    responses = [
        {
            "from": "oncall_engineer",
            "message": "Acknowledged - investigating now",
            "timestamp": datetime.now()
        }
    ]
    
    state.update({
        "messages_received": state.get("messages_received", []) + responses
    })
    return state


async def _escalate_if_needed(state: CommunicationState) -> CommunicationState:
    """Escalate if needed."""
    # Simple escalation logic
    current_level = state.get("escalation_level", 0)
    
    if current_level < 2:  # Max escalation level
        state.update({
            "escalation_level": current_level + 1
        })
    
    return state


async def _complete_communication(state: CommunicationState) -> CommunicationState:
    """Complete the communication process."""
    state.update({
        "status": "completed"
    })
    return state


# Execution subgraph functions
async def _start_execution(state: ExecutionState) -> ExecutionState:
    """Start the execution process."""
    state.update({
        "status": "executing"
    })
    return state


async def _plan_actions(state: ExecutionState) -> ExecutionState:
    """Plan the actions to execute."""
    # Simulate action planning
    planned_actions = [
        {
            "action_id": "action-001",
            "description": "Increase GraphQL service memory limit",
            "priority": "high",
            "estimated_duration": "5 minutes"
        },
        {
            "action_id": "action-002", 
            "description": "Rollback backend configuration changes",
            "priority": "high",
            "estimated_duration": "10 minutes"
        }
    ]
    
    state.update({
        "actions_planned": planned_actions
    })
    return state


async def _allocate_resources(state: ExecutionState) -> ExecutionState:
    """Allocate resources for execution."""
    resources = {
        "memory": "1GB additional",
        "cpu": "2 cores",
        "storage": "10GB",
        "network": "high_bandwidth"
    }
    
    state.update({
        "resources_allocated": resources
    })
    return state


async def _execute_actions(state: ExecutionState) -> ExecutionState:
    """Execute the planned actions."""
    planned_actions = state.get("actions_planned", [])
    executed_actions = []
    
    for action in planned_actions:
        # Simulate action execution
        executed_action = {
            **action,
            "status": "completed",
            "execution_time": datetime.now(),
            "result": "success"
        }
        executed_actions.append(executed_action)
    
    state.update({
        "actions_executed": executed_actions,
        "progress": 1.0  # All actions completed
    })
    return state


async def _monitor_progress(state: ExecutionState) -> ExecutionState:
    """Monitor execution progress."""
    # Simulate progress monitoring
    progress = state.get("progress", 0.0)
    
    if progress >= 1.0:
        state.update({
            "status": "monitoring_complete"
        })
    
    return state


async def _handle_failures(state: ExecutionState) -> ExecutionState:
    """Handle execution failures."""
    # Simulate failure handling
    failed_actions = state.get("actions_failed", [])
    
    if failed_actions:
        # Retry failed actions
        state.update({
            "status": "handling_failures"
        })
    else:
        state.update({
            "status": "no_failures"
        })
    
    return state


async def _complete_execution(state: ExecutionState) -> ExecutionState:
    """Complete the execution process."""
    state.update({
        "status": "completed"
    })
    return state
