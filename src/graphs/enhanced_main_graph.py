"""
Enhanced Main Graph for LangGraph Incident Response System.
Integrates GitHub and Jira MCP capabilities for comprehensive incident response.
"""

import asyncio
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

from langgraph import StateGraph, END
from langgraph.graph import START

from ..types.state import (
    IncidentState,
    IncidentSeverity,
    IncidentStatus,
    AgentRole,
    InvestigationFinding,
    Recommendation
)
from ..agents.incident_response_agent import IncidentResponseAgent
from ..agents.coordinator_agent import CoordinatorAgent


class EnhancedIncidentResponseGraph:
    """
    Enhanced Incident Response Graph with GitHub and Jira MCP Integration.
    This graph orchestrates a comprehensive incident response workflow.
    """
    
    def __init__(self):
        # Initialize Circuit LLM
        try:
            from circuit_llm_client import CircuitLLMWrapper
            circuit_wrapper = CircuitLLMWrapper()
            
            class CircuitLLM:
                def __init__(self, wrapper):
                    self.wrapper = wrapper
                
                async def invoke(self, input_text: str) -> str:
                    return await self.wrapper.invoke(input_text)
                
                async def ainvoke(self, input_text: str) -> str:
                    return await self.wrapper.ainvoke(input_text)
            
            self.llm = CircuitLLM(circuit_wrapper)
        except ImportError:
            # Fallback to OpenAI if Circuit LLM is not available
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.1,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        
        # Initialize agents
        self.coordinator_agent = CoordinatorAgent(agent_id="coordinator-001")
        self.incident_response_agent = IncidentResponseAgent(agent_id="investigator-001")
        
        # Create the graph
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create the enhanced incident response graph."""
        
        # Define the workflow
        workflow = StateGraph(IncidentState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_incident)
        workflow.add_node("coordinate", self._coordinate_response)
        workflow.add_node("investigate", self._investigate_incident)
        workflow.add_node("analyze", self._analyze_findings)
        workflow.add_node("recommend", self._generate_recommendations)
        workflow.add_node("execute", self._execute_actions)
        workflow.add_node("communicate", self._communicate_status)
        workflow.add_node("finalize", self._finalize_incident)
        
        # Define edges
        workflow.add_edge(START, "initialize")
        workflow.add_edge("initialize", "coordinate")
        workflow.add_edge("coordinate", "investigate")
        workflow.add_edge("investigate", "analyze")
        workflow.add_edge("analyze", "recommend")
        workflow.add_edge("recommend", "execute")
        workflow.add_edge("execute", "communicate")
        workflow.add_edge("communicate", "finalize")
        workflow.add_edge("finalize", END)
        
        # Add conditional edges for escalation
        workflow.add_conditional_edges(
            "coordinate",
            self._should_escalate,
            {
                "escalate": "communicate",
                "continue": "investigate"
            }
        )
        
        workflow.add_conditional_edges(
            "analyze",
            self._should_execute_immediately,
            {
                "immediate": "execute",
                "normal": "recommend"
            }
        )
        
        return workflow.compile()
    
    async def _initialize_incident(self, state: IncidentState) -> Dict[str, Any]:
        """Initialize the incident response process."""
        print("🚨 Initializing Incident Response...")
        
        incident_data = state.get('incident', {})
        
        # Create initial state
        initial_state = {
            'incident_id': incident_data.get('id', str(uuid.uuid4())),
            'status': IncidentStatus.INITIALIZED,
            'severity': incident_data.get('severity', IncidentSeverity.MEDIUM),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'assigned_agents': [],
            'completed_steps': ['initialization'],
            'findings': [],
            'recommendations': [],
            'actions_taken': [],
            'communications': []
        }
        
        # Initialize MCP integrations
        await self.incident_response_agent.initialize_integrations()
        
        print(f"✅ Incident initialized: {initial_state['incident_id']}")
        return initial_state
    
    async def _coordinate_response(self, state: IncidentState) -> Dict[str, Any]:
        """Coordinate the incident response with the coordinator agent."""
        print("👥 Coordinating Incident Response...")
        
        try:
            # Execute coordinator agent
            coordinator_result = await self.coordinator_agent.execute(state)
            
            # Update state with coordination results
            updated_state = state.copy()
            updated_state.update({
                'status': IncidentStatus.COORDINATING,
                'updated_at': datetime.now(),
                'completed_steps': state.get('completed_steps', []) + ['coordination'],
                'assigned_agents': coordinator_result.get('assigned_agents', []),
                'coordination_plan': coordinator_result.get('coordination_plan', {})
            })
            
            print("✅ Coordination completed")
            return updated_state
            
        except Exception as e:
            print(f"❌ Coordination error: {e}")
            return state
    
    async def _investigate_incident(self, state: IncidentState) -> Dict[str, Any]:
        """Investigate the incident using the enhanced incident response agent."""
        print("🔍 Investigating Incident...")
        
        try:
            # Execute incident response agent
            investigation_result = await self.incident_response_agent.execute(state)
            
            # Update state with investigation results
            updated_state = state.copy()
            updated_state.update({
                'status': investigation_result.get('status', IncidentStatus.INVESTIGATING),
                'updated_at': datetime.now(),
                'completed_steps': state.get('completed_steps', []) + ['investigation'],
                'findings': investigation_result.get('findings', []),
                'jira_tickets': investigation_result.get('jira_tickets', [])
            })
            
            print(f"✅ Investigation completed: {len(updated_state['findings'])} findings")
            return updated_state
            
        except Exception as e:
            print(f"❌ Investigation error: {e}")
            return state
    
    async def _analyze_findings(self, state: IncidentState) -> Dict[str, Any]:
        """Analyze investigation findings and determine next steps."""
        print("📊 Analyzing Findings...")
        
        findings = state.get('findings', [])
        
        # Analyze findings using LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are an expert incident response analyst. Analyze the investigation findings
            and determine the severity, root cause, and required actions.
            """),
            ("human", """
            Analyze these investigation findings:
            
            {findings}
            
            Provide analysis as JSON:
            {{
                "root_cause": "string",
                "severity_assessment": "high|medium|low",
                "immediate_actions_required": true|false,
                "escalation_needed": true|false,
                "confidence": 0.0-1.0,
                "analysis_summary": "string"
            }}
            """)
        ])
        
        try:
            chain = prompt | self.llm | JsonOutputParser()
            analysis = await chain.ainvoke({
                "findings": self._format_findings_for_analysis(findings)
            })
            
            # Update state with analysis
            updated_state = state.copy()
            updated_state.update({
                'status': IncidentStatus.ANALYZING,
                'updated_at': datetime.now(),
                'completed_steps': state.get('completed_steps', []) + ['analysis'],
                'analysis': analysis
            })
            
            print(f"✅ Analysis completed: {analysis.get('root_cause', 'Unknown')}")
            return updated_state
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return state
    
    async def _generate_recommendations(self, state: IncidentState) -> Dict[str, Any]:
        """Generate recommendations based on analysis."""
        print("💡 Generating Recommendations...")
        
        findings = state.get('findings', [])
        analysis = state.get('analysis', {})
        
        # Use the incident response agent to generate recommendations
        try:
            recommendations = await self.incident_response_agent._generate_recommendations(state, findings)
            
            # Update state with recommendations
            updated_state = state.copy()
            updated_state.update({
                'status': IncidentStatus.RECOMMENDING,
                'updated_at': datetime.now(),
                'completed_steps': state.get('completed_steps', []) + ['recommendations'],
                'recommendations': recommendations
            })
            
            print(f"✅ Recommendations generated: {len(recommendations)}")
            return updated_state
            
        except Exception as e:
            print(f"❌ Recommendation generation error: {e}")
            return state
    
    async def _execute_actions(self, state: IncidentState) -> Dict[str, Any]:
        """Execute recommended actions."""
        print("⚡ Executing Actions...")
        
        recommendations = state.get('recommendations', [])
        actions_taken = []
        
        # Execute high-priority recommendations
        for recommendation in recommendations:
            if recommendation.priority == "high":
                try:
                    action_result = await self._execute_recommendation(recommendation, state)
                    actions_taken.append(action_result)
                except Exception as e:
                    print(f"❌ Error executing recommendation {recommendation.id}: {e}")
        
        # Update state with executed actions
        updated_state = state.copy()
        updated_state.update({
            'status': IncidentStatus.EXECUTING,
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['execution'],
            'actions_taken': actions_taken
        })
        
        print(f"✅ Actions executed: {len(actions_taken)}")
        return updated_state
    
    async def _execute_recommendation(self, recommendation: Recommendation, state: IncidentState) -> Dict[str, Any]:
        """Execute a specific recommendation."""
        print(f"🔧 Executing: {recommendation.title}")
        
        # This would typically involve actual system actions
        # For now, we'll simulate the execution
        action_result = {
            'id': str(uuid.uuid4()),
            'recommendation_id': recommendation.id,
            'title': recommendation.title,
            'status': 'completed',
            'executed_at': datetime.now(),
            'result': 'Action executed successfully'
        }
        
        return action_result
    
    async def _communicate_status(self, state: IncidentState) -> Dict[str, Any]:
        """Communicate incident status to stakeholders."""
        print("📢 Communicating Status...")
        
        incident_data = state.get('incident', {})
        findings = state.get('findings', [])
        recommendations = state.get('recommendations', [])
        
        # Generate communication message
        communication = {
            'id': str(uuid.uuid4()),
            'type': 'status_update',
            'timestamp': datetime.now(),
            'message': f"""
            Incident Status Update:
            
            Incident: {incident_data.get('title', 'Unknown')}
            Status: {state.get('status', 'Unknown')}
            Severity: {state.get('severity', 'Unknown')}
            
            Findings: {len(findings)} discovered
            Recommendations: {len(recommendations)} generated
            Actions: {len(state.get('actions_taken', []))} executed
            
            Next Steps: {self._get_next_steps(state)}
            """
        }
        
        # Update state with communication
        updated_state = state.copy()
        updated_state.update({
            'status': IncidentStatus.COMMUNICATING,
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['communication'],
            'communications': state.get('communications', []) + [communication]
        })
        
        print("✅ Status communicated")
        return updated_state
    
    async def _finalize_incident(self, state: IncidentState) -> Dict[str, Any]:
        """Finalize the incident response process."""
        print("🏁 Finalizing Incident Response...")
        
        # Determine final status
        if state.get('status') == IncidentStatus.EXECUTING:
            final_status = IncidentStatus.RESOLVED
        else:
            final_status = IncidentStatus.CLOSED
        
        # Update state
        updated_state = state.copy()
        updated_state.update({
            'status': final_status,
            'updated_at': datetime.now(),
            'completed_steps': state.get('completed_steps', []) + ['finalization'],
            'resolved_at': datetime.now()
        })
        
        print(f"✅ Incident finalized: {final_status}")
        return updated_state
    
    def _should_escalate(self, state: IncidentState) -> str:
        """Determine if escalation is needed."""
        severity = state.get('severity', IncidentSeverity.MEDIUM)
        findings = state.get('findings', [])
        
        # Escalate if high severity or high-severity findings
        if severity == IncidentSeverity.HIGH or any(f.severity == "high" for f in findings):
            return "escalate"
        return "continue"
    
    def _should_execute_immediately(self, state: IncidentState) -> str:
        """Determine if immediate execution is needed."""
        analysis = state.get('analysis', {})
        
        if analysis.get('immediate_actions_required', False):
            return "immediate"
        return "normal"
    
    def _format_findings_for_analysis(self, findings: List[InvestigationFinding]) -> str:
        """Format findings for analysis."""
        if not findings:
            return "No findings available."
        
        formatted = []
        for i, finding in enumerate(findings, 1):
            formatted.append(f"""
            Finding {i}:
            - Title: {finding.title}
            - Severity: {finding.severity}
            - Confidence: {finding.confidence:.1%}
            - Description: {finding.description}
            - Evidence: {finding.evidence}
            """)
        
        return '\n'.join(formatted)
    
    def _get_next_steps(self, state: IncidentState) -> str:
        """Get next steps based on current state."""
        status = state.get('status', IncidentStatus.INITIALIZED)
        
        if status == IncidentStatus.INITIALIZED:
            return "Begin investigation and coordination"
        elif status == IncidentStatus.INVESTIGATING:
            return "Complete investigation and analyze findings"
        elif status == IncidentStatus.ANALYZING:
            return "Generate recommendations and plan actions"
        elif status == IncidentStatus.EXECUTING:
            return "Monitor action execution and communicate status"
        else:
            return "Finalize incident and document lessons learned"
    
    async def run_incident_response(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete incident response workflow."""
        print("🚀 Starting Enhanced Incident Response Workflow...")
        
        # Create initial state
        initial_state = {
            'incident': incident_data,
            'incident_id': incident_data.get('id', str(uuid.uuid4())),
            'status': IncidentStatus.INITIALIZED,
            'severity': incident_data.get('severity', IncidentSeverity.MEDIUM),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'assigned_agents': [],
            'completed_steps': [],
            'findings': [],
            'recommendations': [],
            'actions_taken': [],
            'communications': []
        }
        
        try:
            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            print("🎉 Enhanced Incident Response Workflow Completed!")
            return final_state
            
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            return initial_state


# Import os for environment variables
import os
