"""
Main LangGraph workflow for the Incident Response System.
Following patterns from Module 4 Research Assistant with parallelization and subgraphs.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import os

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from ..types.state import (
    IncidentState,
    InvestigationState,
    AnalysisState,
    CommunicationState,
    ExecutionState,
    CoordinatorState,
    IncidentSeverity,
    IncidentStatus
)
from ..agents.coordinator_agent import CoordinatorAgent
from ..services.langchain_mcp_client import langchain_mcp_client
from .subgraphs import (
    create_investigation_subgraph,
    create_analysis_subgraph,
    create_communication_subgraph,
    create_execution_subgraph
)


class IncidentResponseGraph:
    """
    Main incident response workflow graph.
    Following patterns from Module 4 Research Assistant.
    """
    
    def __init__(self):
        self.graph = None
        self.coordinator = None
        self.memory_saver = MemorySaver()
        self.mcp_initialized = False
        self._build_graph()
    
    async def initialize_mcp_connections(self):
        """Initialize LangChain MCP connections to external servers."""
        if self.mcp_initialized:
            return
        
        try:
            # Initialize LangChain MCP client with external servers
            config = {
                "github_mcp_url": os.getenv("MCP_GITHUB_SERVER_URL"),
                "jira_mcp_url": os.getenv("MCP_JIRA_SERVER_URL"),
                "github_token": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
                "jira_token": os.getenv("JIRA_TOKEN")
            }
            
            success = await langchain_mcp_client.initialize(config)
            
            if success:
                self.mcp_initialized = True
                print("✅ LangChain MCP connections initialized successfully")
            else:
                print("⚠️  LangChain MCP initialization failed")
                print("Continuing with simulated data...")
            
        except Exception as e:
            print(f"⚠️  LangChain MCP initialization failed: {e}")
            print("Continuing with simulated data...")
    
    def _build_graph(self):
        """Build the main incident response workflow graph."""
        
        # Initialize coordinator agent
        self.coordinator = CoordinatorAgent(agent_id="coordinator-001")
        
        # Create the main state graph
        builder = StateGraph(IncidentState)
        
        # Add nodes
        builder.add_node("initialize_incident", self._initialize_incident)
        builder.add_node("initialize_mcp", self._initialize_mcp)
        builder.add_node("coordinator_assessment", self._coordinator_assessment)
        builder.add_node("parallel_investigation", self._parallel_investigation)
        builder.add_node("parallel_analysis", self._parallel_analysis)
        builder.add_node("parallel_communication", self._parallel_communication)
        builder.add_node("synthesize_results", self._synthesize_results)
        builder.add_node("decision_point", self._decision_point)
        builder.add_node("parallel_execution", self._parallel_execution)
        builder.add_node("create_jira_ticket", self._create_jira_ticket)
        builder.add_node("finalize_incident", self._finalize_incident)
        
        # Add edges
        builder.add_edge(START, "initialize_incident")
        builder.add_edge("initialize_incident", "initialize_mcp")
        builder.add_edge("initialize_mcp", "coordinator_assessment")
        builder.add_edge("coordinator_assessment", "parallel_investigation")
        builder.add_edge("coordinator_assessment", "parallel_analysis")
        builder.add_edge("coordinator_assessment", "parallel_communication")
        builder.add_edge("parallel_investigation", "synthesize_results")
        builder.add_edge("parallel_analysis", "synthesize_results")
        builder.add_edge("parallel_communication", "synthesize_results")
        builder.add_edge("synthesize_results", "decision_point")
        builder.add_edge("decision_point", "parallel_execution")
        builder.add_edge("parallel_execution", "create_jira_ticket")
        builder.add_edge("create_jira_ticket", "finalize_incident")
        builder.add_edge("finalize_incident", END)
        
        # Compile the graph
        self.graph = builder.compile(checkpointer=self.memory_saver)
    
    async def _initialize_incident(self, state: IncidentState) -> IncidentState:
        """Initialize the incident with basic information."""
        incident_id = state.get("incident_id", f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        
        # Initialize memory collection
        from ..types.state import MemoryCollection
        memory_collection = MemoryCollection(
            incident_id=incident_id,
            memories=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Update state
        state.update({
            "incident_id": incident_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status": IncidentStatus.OPEN,
            "active_agents": [],
            "agent_profiles": {},
            "memories": memory_collection,
            "context": {},
            "messages": [],
            "notifications": [],
            "current_step": "initialized",
            "completed_steps": ["initialized"],
            "next_actions": ["initialize_mcp"]
        })
        
        return state
    
    async def _initialize_mcp(self, state: IncidentState) -> IncidentState:
        """Initialize MCP connections."""
        await self.initialize_mcp_connections()
        
        state.update({
            "updated_at": datetime.now(),
            "current_step": "mcp_initialized",
            "completed_steps": state.get("completed_steps", []) + ["mcp_initialized"],
            "next_actions": ["coordinator_assessment"],
            "context": {
                **state.get("context", {}),
                "mcp_available": self.mcp_initialized
            }
        })
        
        return state
    
    async def _coordinator_assessment(self, state: IncidentState) -> IncidentState:
        """Coordinator assesses the incident and creates initial plan."""
        
        # Execute coordinator logic
        coordinator_result = await self.coordinator.execute(state)
        
        # Update state with coordinator decisions
        state.update({
            "updated_at": datetime.now(),
            "current_step": "coordinator_assessment",
            "completed_steps": state.get("completed_steps", []) + ["coordinator_assessment"],
            "next_actions": coordinator_result.get("updates", {}).get("next_actions", []),
            "context": {
                **state.get("context", {}),
                "coordinator_assessment": coordinator_result
            }
        })
        
        # Add coordinator memory
        if state.get("memories"):
            state["memories"].memories.append(
                coordinator_result.get("updates", {}).get("coordination_plan", {}).get("summary", "")
            )
        
        return state
    
    async def _parallel_investigation(self, state: IncidentState) -> IncidentState:
        """Execute investigation in parallel using subgraph."""
        
        # Create investigation subgraph
        investigation_graph = create_investigation_subgraph()
        
        # Prepare investigation state
        investigation_state = InvestigationState(
            incident_id=state.get("incident_id"),
            investigator_id="investigator-001",
            focus_area="root_cause_analysis",
            findings=state.get("findings", []),
            evidence=[],
            analysis_notes=[],
            confidence_level=0.0,
            status="started"
        )
        
        # Execute investigation subgraph
        investigation_result = await investigation_graph.ainvoke(investigation_state)
        
        # Update main state with investigation results
        state.update({
            "updated_at": datetime.now(),
            "findings": investigation_result.get("findings", []),
            "current_step": "investigation_completed",
            "completed_steps": state.get("completed_steps", []) + ["investigation"],
            "context": {
                **state.get("context", {}),
                "investigation_results": investigation_result
            }
        })
        
        return state
    
    async def _parallel_analysis(self, state: IncidentState) -> IncidentState:
        """Execute analysis in parallel using subgraph."""
        
        # Create analysis subgraph
        analysis_graph = create_analysis_subgraph()
        
        # Prepare analysis state
        analysis_state = AnalysisState(
            incident_id=state.get("incident_id"),
            analyst_id="analyst-001",
            data_sources=state.get("affected_services", []),
            analysis_results=[],
            patterns=[],
            correlations=[],
            insights=[],
            status="started"
        )
        
        # Execute analysis subgraph
        analysis_result = await analysis_graph.ainvoke(analysis_state)
        
        # Update main state with analysis results
        state.update({
            "updated_at": datetime.now(),
            "current_step": "analysis_completed",
            "completed_steps": state.get("completed_steps", []) + ["analysis"],
            "context": {
                **state.get("context", {}),
                "analysis_results": analysis_result
            }
        })
        
        return state
    
    async def _parallel_communication(self, state: IncidentState) -> IncidentState:
        """Execute communication in parallel using subgraph."""
        
        # Create communication subgraph
        communication_graph = create_communication_subgraph()
        
        # Prepare communication state
        communication_state = CommunicationState(
            incident_id=state.get("incident_id"),
            communicator_id="communicator-001",
            stakeholders=["engineering", "management", "customers"],
            messages_sent=[],
            messages_received=[],
            escalation_level=0,
            communication_plan={},
            status="started"
        )
        
        # Execute communication subgraph
        communication_result = await communication_graph.ainvoke(communication_state)
        
        # Update main state with communication results
        state.update({
            "updated_at": datetime.now(),
            "current_step": "communication_completed",
            "completed_steps": state.get("completed_steps", []) + ["communication"],
            "messages": communication_result.get("messages_sent", []),
            "notifications": communication_result.get("messages_received", []),
            "context": {
                **state.get("context", {}),
                "communication_results": communication_result
            }
        })
        
        return state
    
    async def _synthesize_results(self, state: IncidentState) -> IncidentState:
        """Synthesize results from all parallel processes."""
        
        # Get results from all subgraphs
        investigation_results = state.get("context", {}).get("investigation_results", {})
        analysis_results = state.get("context", {}).get("analysis_results", {})
        communication_results = state.get("context", {}).get("communication_results", {})
        
        # Synthesize findings and recommendations
        synthesis_task = f"""
        Synthesize results from all incident response activities:
        
        Investigation Results: {investigation_results}
        Analysis Results: {analysis_results}
        Communication Results: {communication_results}
        
        Create a comprehensive synthesis including:
        1. Key findings summary
        2. Root cause analysis
        3. Impact assessment
        4. Recommendations
        5. Next steps
        """
        
        synthesis_result = await self.coordinator.process_task(state, synthesis_task)
        
        # Update state with synthesis
        state.update({
            "updated_at": datetime.now(),
            "current_step": "synthesis_completed",
            "completed_steps": state.get("completed_steps", []) + ["synthesis"],
            "next_actions": ["decision_point"],
            "context": {
                **state.get("context", {}),
                "synthesis": synthesis_result
            }
        })
        
        return state
    
    async def _decision_point(self, state: IncidentState) -> IncidentState:
        """Decision point for next actions."""
        
        # Get synthesis results
        synthesis = state.get("context", {}).get("synthesis", {})
        
        # Make decision about next steps
        decision_task = f"""
        Based on the incident synthesis, determine the next course of action:
        
        Synthesis: {synthesis.get('full_response', '')}
        Current Status: {state.get('status')}
        Severity: {state.get('severity')}
        
        Options:
        1. Execute immediate fixes
        2. Escalate to management
        3. Continue investigation
        4. Close incident
        
        Provide decision with justification.
        """
        
        decision_result = await self.coordinator.process_task(state, decision_task)
        
        # Update state with decision
        state.update({
            "updated_at": datetime.now(),
            "current_step": "decision_made",
            "completed_steps": state.get("completed_steps", []) + ["decision"],
            "next_actions": ["parallel_execution"],
            "context": {
                **state.get("context", {}),
                "decision": decision_result
            }
        })
        
        return state
    
    async def _parallel_execution(self, state: IncidentState) -> IncidentState:
        """Execute actions in parallel using subgraph."""
        
        # Create execution subgraph
        execution_graph = create_execution_subgraph()
        
        # Prepare execution state
        execution_state = ExecutionState(
            incident_id=state.get("incident_id"),
            executor_id="executor-001",
            actions_planned=state.get("next_actions", []),
            actions_executed=[],
            actions_failed=[],
            resources_allocated={},
            progress=0.0,
            status="started"
        )
        
        # Execute execution subgraph
        execution_result = await execution_graph.ainvoke(execution_state)
        
        # Update main state with execution results
        state.update({
            "updated_at": datetime.now(),
            "current_step": "execution_completed",
            "completed_steps": state.get("completed_steps", []) + ["execution"],
            "status": IncidentStatus.RESOLVED if execution_result.get("progress", 0) >= 1.0 else IncidentStatus.INVESTIGATING,
            "context": {
                **state.get("context", {}),
                "execution_results": execution_result
            }
        })
        
        return state
    
    async def _create_jira_ticket(self, state: IncidentState) -> IncidentState:
        """Create Jira ticket with incident details using MCP."""
        
        if not self.mcp_initialized:
            print("⚠️  MCP not available - skipping Jira ticket creation")
            return state
        
        try:
            # Prepare incident summary for Jira
            incident_summary = f"Incident {state.get('incident_id')}: {state.get('title')}"
            
            # Create detailed description
            findings = state.get("findings", [])
            recommendations = state.get("recommendations", [])
            
            description = f"""
            **Incident Details:**
            - ID: {state.get('incident_id')}
            - Title: {state.get('title')}
            - Severity: {state.get('severity')}
            - Status: {state.get('status')}
            - Affected Services: {', '.join(state.get('affected_services', []))}
            
            **Findings ({len(findings)}):**
            {chr(10).join([f"- {f.get('title', 'Unknown')}: {f.get('description', 'No description')}" for f in findings])}
            
            **Recommendations ({len(recommendations)}):**
            {chr(10).join([f"- {r.get('title', 'Unknown')}: {r.get('description', 'No description')}" for r in recommendations])}
            
            **Timeline:**
            - Created: {state.get('created_at')}
            - Updated: {state.get('updated_at')}
            - Completed Steps: {', '.join(state.get('completed_steps', []))}
            """
            
            # Create Jira issue using MCP
            issue_key = await langchain_mcp_client.create_jira_issue(
                summary=incident_summary,
                description=description,
                issue_type="Incident"
            )
            
            if issue_key:
                # Add comment with synthesis
                synthesis = state.get("context", {}).get("synthesis", {})
                if synthesis:
                    await langchain_mcp_client.add_jira_comment(
                        issue_key=issue_key,
                        comment=f"**Incident Synthesis:**\n{synthesis.get('summary', 'No synthesis available')}"
                    )
                
                state.update({
                    "updated_at": datetime.now(),
                    "current_step": "jira_ticket_created",
                    "completed_steps": state.get("completed_steps", []) + ["jira_ticket_created"],
                    "context": {
                        **state.get("context", {}),
                        "jira_ticket_key": issue_key
                    }
                })
                
                print(f"✅ Jira ticket created: {issue_key}")
            else:
                print("❌ Failed to create Jira ticket")
            
        except Exception as e:
            print(f"❌ Error creating Jira ticket: {e}")
        
        return state
    
    async def _finalize_incident(self, state: IncidentState) -> IncidentState:
        """Finalize the incident response."""
        
        # Create final summary
        finalization_task = f"""
        Create a final summary for incident {state.get('incident_id')}:
        
        Incident: {state.get('title')}
        Status: {state.get('status')}
        Completed Steps: {state.get('completed_steps', [])}
        Findings: {len(state.get('findings', []))}
        Recommendations: {len(state.get('recommendations', []))}
        
        Provide:
        1. Executive summary
        2. Key learnings
        3. Follow-up actions
        4. Prevention measures
        """
        
        finalization_result = await self.coordinator.process_task(state, finalization_task)
        
        # Update state for finalization
        state.update({
            "updated_at": datetime.now(),
            "current_step": "finalized",
            "completed_steps": state.get("completed_steps", []) + ["finalized"],
            "status": IncidentStatus.CLOSED,
            "context": {
                **state.get("context", {}),
                "finalization": finalization_result
            }
        })
        
        return state
    
    async def run_incident_response(self, incident_data: Dict[str, Any]) -> IncidentState:
        """Run the complete incident response workflow."""
        
        # Initialize state with incident data
        initial_state = IncidentState(
            incident_id=incident_data.get("incident_id"),
            title=incident_data.get("title", ""),
            description=incident_data.get("description", ""),
            severity=incident_data.get("severity", IncidentSeverity.MEDIUM),
            status=IncidentStatus.OPEN,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            affected_services=incident_data.get("affected_services", []),
            git_commits=[],
            service_logs=[],
            findings=[],
            recommendations=[],
            active_agents=[],
            agent_profiles={},
            memories=None,  # Will be initialized in the graph
            context={},
            messages=[],
            notifications=[],
            current_step="",
            completed_steps=[],
            next_actions=[]
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return final_state
    
    def get_graph_visualization(self) -> str:
        """Get a visualization of the graph structure."""
        return self.graph.get_graph().draw_mermaid_png()
    
    async def cleanup(self):
        """Cleanup MCP connections."""
        await langchain_mcp_client.close()
