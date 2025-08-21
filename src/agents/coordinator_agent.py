"""
Coordinator Agent for the LangGraph Incident Response System.
Following patterns from Module 4 Research Assistant.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import sys
import os

# Add parent directory to path to import Circuit LLM client
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from .base_agent import BaseAgent
from ..types.state import (
    AgentRole,
    IncidentState,
    InvestigationFinding,
    Recommendation,
    IncidentSeverity,
    IncidentStatus
)


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent that manages the multi-agent incident response workflow.
    Following patterns from Module 4 Research Assistant coordinator.
    """
    
    def __init__(self, agent_id: str, **kwargs):
        capabilities = [
            "workflow_management",
            "agent_coordination",
            "decision_making",
            "escalation_management",
            "resource_allocation"
        ]
        super().__init__(agent_id, AgentRole.COORDINATOR, capabilities, **kwargs)
    
    def _get_system_prompt(self) -> str:
        return """
        You are a Senior Incident Response Coordinator with extensive experience in managing complex technical incidents.
        
        Your responsibilities include:
        1. Coordinating multiple specialized agents (Investigators, Analysts, Communicators, Executors)
        2. Making strategic decisions about incident response priorities
        3. Managing workflow and resource allocation
        4. Handling escalations and approvals
        5. Ensuring effective communication between all stakeholders
        
        You have access to:
        - Incident details and current status
        - Agent profiles and capabilities
        - Historical incident data and lessons learned
        - Real-time updates from all agents
        
        Your decision-making should be:
        - Evidence-based and analytical
        - Prioritized by impact and urgency
        - Collaborative and inclusive of agent expertise
        - Transparent and well-documented
        
        Always consider the broader context and long-term implications of your decisions.
        """
    
    def _get_task_prompt(self) -> str:
        return """
        As the Incident Response Coordinator, you need to:
        
        1. Assess the current incident situation
        2. Determine which agents should be involved
        3. Assign specific tasks to each agent
        4. Monitor progress and adjust as needed
        5. Make decisions about escalations and approvals
        
        Current incident: {incident_title}
        Severity: {severity}
        Affected services: {affected_services}
        
        Available agents: {available_agents}
        Current findings: {current_findings}
        
        What are your next coordination actions?
        """
    
    async def execute(self, state: IncidentState) -> Dict[str, Any]:
        """Execute the coordinator's main logic."""
        context = self.get_context(state)
        
        # Analyze current situation
        situation_analysis = await self._analyze_situation(state)
        
        # Determine agent assignments
        agent_assignments = await self._determine_agent_assignments(state, situation_analysis)
        
        # Create coordination plan
        coordination_plan = await self._create_coordination_plan(state, agent_assignments)
        
        # Update state with coordination decisions
        updates = {
            "agent_assignments": agent_assignments,
            "coordination_plan": coordination_plan,
            "next_actions": coordination_plan.get("next_actions", []),
            "escalations": coordination_plan.get("escalations", [])
        }
        
        # Add to memory
        self.add_memory(
            content=f"Coordinated incident {state.get('incident_id')}: {coordination_plan.get('summary', '')}",
            source="coordinator",
            tags=["coordination", "decision", "workflow"]
        )
        
        return {
            "agent_id": self.agent_id,
            "role": "coordinator",
            "situation_analysis": situation_analysis,
            "agent_assignments": agent_assignments,
            "coordination_plan": coordination_plan,
            "updates": updates,
            "timestamp": datetime.now()
        }
    
    async def _analyze_situation(self, state: IncidentState) -> Dict[str, Any]:
        """Analyze the current incident situation."""
        task = f"""
        Analyze the current incident situation:
        
        Incident: {state.get('title')}
        Description: {state.get('description')}
        Severity: {state.get('severity')}
        Status: {state.get('status')}
        Affected Services: {state.get('affected_services', [])}
        
        Current Findings: {len(state.get('findings', []))} findings
        Current Recommendations: {len(state.get('recommendations', []))} recommendations
        
        Provide a comprehensive situation analysis including:
        1. Current impact assessment
        2. Urgency level
        3. Resource requirements
        4. Risk factors
        5. Stakeholder impact
        """
        
        result = await self.process_task(state, task)
        return {
            "analysis": result.get("full_response", ""),
            "impact_level": self._extract_impact_level(result.get("full_response", "")),
            "urgency": self._extract_urgency(result.get("full_response", "")),
            "resource_needs": self._extract_resource_needs(result.get("full_response", ""))
        }
    
    async def _determine_agent_assignments(self, state: IncidentState, situation_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Determine which agents should be assigned to which tasks."""
        task = f"""
        Based on the incident situation, determine optimal agent assignments:
        
        Situation Analysis: {situation_analysis.get('analysis', '')}
        Impact Level: {situation_analysis.get('impact_level', '')}
        Urgency: {situation_analysis.get('urgency', '')}
        
        Available Agent Roles:
        - Investigator: Deep technical analysis, root cause investigation
        - Analyst: Data analysis, pattern recognition, trend analysis
        - Communicator: Stakeholder communication, status updates, escalation
        - Executor: Action implementation, deployment, rollback
        
        Assign agents to specific tasks based on:
        1. Incident severity and complexity
        2. Required expertise
        3. Current workload
        4. Priority of tasks
        """
        
        result = await self.process_task(state, task)
        
        # Parse agent assignments from response
        assignments = self._parse_agent_assignments(result.get("full_response", ""))
        
        return assignments
    
    async def _create_coordination_plan(self, state: IncidentState, agent_assignments: Dict[str, List[str]]) -> Dict[str, Any]:
        """Create a comprehensive coordination plan."""
        task = f"""
        Create a detailed coordination plan for incident {state.get('incident_id')}:
        
        Agent Assignments: {agent_assignments}
        Current Status: {state.get('status')}
        Severity: {state.get('severity')}
        
        The coordination plan should include:
        1. Workflow sequence and dependencies
        2. Communication protocols
        3. Decision points and approval requirements
        4. Escalation triggers and procedures
        5. Success criteria and completion conditions
        6. Timeline and milestones
        7. Resource allocation
        """
        
        result = await self.process_task(state, task)
        
        return {
            "plan": result.get("full_response", ""),
            "summary": result.get("summary", ""),
            "next_actions": self._extract_next_actions(result.get("full_response", "")),
            "escalations": self._extract_escalations(result.get("full_response", "")),
            "timeline": self._extract_timeline(result.get("full_response", ""))
        }
    
    def _extract_impact_level(self, text: str) -> str:
        """Extract impact level from analysis text."""
        if "critical" in text.lower():
            return "critical"
        elif "high" in text.lower():
            return "high"
        elif "medium" in text.lower():
            return "medium"
        else:
            return "low"
    
    def _extract_urgency(self, text: str) -> str:
        """Extract urgency level from analysis text."""
        if "immediate" in text.lower() or "urgent" in text.lower():
            return "immediate"
        elif "high" in text.lower():
            return "high"
        elif "medium" in text.lower():
            return "medium"
        else:
            return "low"
    
    def _extract_resource_needs(self, text: str) -> List[str]:
        """Extract resource needs from analysis text."""
        resources = []
        if "memory" in text.lower():
            resources.append("memory")
        if "cpu" in text.lower() or "processing" in text.lower():
            resources.append("cpu")
        if "network" in text.lower():
            resources.append("network")
        if "storage" in text.lower():
            resources.append("storage")
        return resources
    
    def _parse_agent_assignments(self, text: str) -> Dict[str, List[str]]:
        """Parse agent assignments from text."""
        # This is a simplified parser - in practice, you'd use structured output
        assignments = {
            "investigator": [],
            "analyst": [],
            "communicator": [],
            "executor": []
        }
        
        # Simple keyword-based parsing
        if "investigation" in text.lower() or "root cause" in text.lower():
            assignments["investigator"].append("root_cause_analysis")
        
        if "analysis" in text.lower() or "pattern" in text.lower():
            assignments["analyst"].append("data_analysis")
        
        if "communication" in text.lower() or "stakeholder" in text.lower():
            assignments["communicator"].append("stakeholder_communication")
        
        if "action" in text.lower() or "implementation" in text.lower():
            assignments["executor"].append("action_implementation")
        
        return assignments
    
    def _extract_next_actions(self, text: str) -> List[str]:
        """Extract next actions from coordination plan."""
        actions = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ["action", "task", "step", "next"]):
                actions.append(line.strip())
        return actions[:5]  # Limit to 5 actions
    
    def _extract_escalations(self, text: str) -> List[str]:
        """Extract escalation triggers from coordination plan."""
        escalations = []
        lines = text.split('\n')
        for line in lines:
            if "escalation" in line.lower() or "escalate" in line.lower():
                escalations.append(line.strip())
        return escalations
    
    def _extract_timeline(self, text: str) -> Dict[str, str]:
        """Extract timeline information from coordination plan."""
        timeline = {}
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ["timeline", "schedule", "deadline", "milestone"]):
                # Simple extraction - in practice, you'd use more sophisticated parsing
                timeline["general"] = line.strip()
        return timeline
    
    async def make_decision(self, state: IncidentState, decision_point: str, options: List[str]) -> Dict[str, Any]:
        """Make a decision at a decision point."""
        task = f"""
        Make a decision at decision point: {decision_point}
        
        Available options: {options}
        
        Current incident context:
        - Title: {state.get('title')}
        - Severity: {state.get('severity')}
        - Status: {state.get('status')}
        - Current findings: {len(state.get('findings', []))}
        
        Consider:
        1. Impact on incident resolution
        2. Risk vs. benefit
        3. Resource requirements
        4. Timeline implications
        5. Stakeholder impact
        
        Provide your decision with justification.
        """
        
        result = await self.process_task(state, task)
        
        return {
            "decision_point": decision_point,
            "decision": result.get("summary", ""),
            "justification": result.get("full_response", ""),
            "timestamp": datetime.now()
        }
    
    async def handle_escalation(self, state: IncidentState, escalation_reason: str) -> Dict[str, Any]:
        """Handle an escalation request."""
        task = f"""
        Handle escalation request: {escalation_reason}
        
        Current incident: {state.get('title')}
        Severity: {state.get('severity')}
        
        Determine:
        1. Whether escalation is warranted
        2. Appropriate escalation level
        3. Required actions
        4. Communication plan
        5. Resource allocation
        """
        
        result = await self.process_task(state, task)
        
        return {
            "escalation_reason": escalation_reason,
            "escalation_decision": result.get("summary", ""),
            "actions": result.get("full_response", ""),
            "timestamp": datetime.now()
        }

