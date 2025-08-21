"""
State definitions for the LangGraph Incident Response System.
Following patterns from LangChain Academy Module 4 & 5.
"""

from typing import List, Optional, Dict, Any, Annotated
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Incident status levels."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AgentRole(str, Enum):
    """Agent roles in the incident response system."""
    COORDINATOR = "coordinator"
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    COMMUNICATOR = "communicator"
    EXECUTOR = "executor"


class GitCommit(BaseModel):
    """Git commit information."""
    sha: str = Field(description="Commit SHA")
    author: str = Field(description="Author name")
    date: datetime = Field(description="Commit date")
    message: str = Field(description="Commit message")
    files: List[str] = Field(description="Files changed")
    repository: str = Field(description="Repository name")


class ServiceLog(BaseModel):
    """Service log entry."""
    timestamp: datetime = Field(description="Log timestamp")
    level: str = Field(description="Log level")
    message: str = Field(description="Log message")
    service: str = Field(description="Service name")
    metadata: Optional[Dict[str, Any]] = Field(description="Additional metadata")


class Memory(BaseModel):
    """Memory entry for the incident response system."""
    content: str = Field(description="The main content of the memory")
    timestamp: datetime = Field(description="When the memory was created")
    source: str = Field(description="Source of the memory (agent, user, system)")
    tags: List[str] = Field(description="Tags for categorization")


class MemoryCollection(BaseModel):
    """Collection of memories for the incident."""
    incident_id: str = Field(description="Associated incident ID")
    memories: List[Memory] = Field(description="List of memories")
    created_at: datetime = Field(description="Collection creation time")
    updated_at: datetime = Field(description="Last update time")


class AgentProfile(BaseModel):
    """Agent profile with preferences and capabilities."""
    agent_id: str = Field(description="Unique agent identifier")
    role: AgentRole = Field(description="Agent role")
    capabilities: List[str] = Field(description="Agent capabilities")
    preferences: Dict[str, Any] = Field(description="Agent preferences")
    performance_metrics: Dict[str, float] = Field(description="Performance metrics")


class InvestigationFinding(BaseModel):
    """Finding from an investigation."""
    finding_id: str = Field(description="Unique finding identifier")
    title: str = Field(description="Finding title")
    description: str = Field(description="Finding description")
    severity: IncidentSeverity = Field(description="Finding severity")
    evidence: List[str] = Field(description="Evidence supporting the finding")
    confidence: float = Field(description="Confidence level (0-1)")
    agent_id: str = Field(description="Agent that made the finding")
    timestamp: datetime = Field(description="When the finding was made")


class Recommendation(BaseModel):
    """Recommendation for incident response."""
    recommendation_id: str = Field(description="Unique recommendation identifier")
    title: str = Field(description="Recommendation title")
    description: str = Field(description="Recommendation description")
    priority: IncidentSeverity = Field(description="Recommendation priority")
    action_items: List[str] = Field(description="Specific action items")
    estimated_effort: str = Field(description="Estimated effort required")
    agent_id: str = Field(description="Agent that made the recommendation")
    timestamp: datetime = Field(description="When the recommendation was made")


class IncidentState(TypedDict):
    """Main state for the incident response system."""
    # Incident information
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    created_at: datetime
    updated_at: datetime
    
    # Affected services
    affected_services: List[str]
    
    # Investigation data
    git_commits: List[GitCommit]
    service_logs: List[ServiceLog]
    findings: List[InvestigationFinding]
    recommendations: List[Recommendation]
    
    # Agent information
    active_agents: List[str]
    agent_profiles: Dict[str, AgentProfile]
    
    # Memory and context
    memories: MemoryCollection
    context: Dict[str, Any]
    
    # Communication
    messages: List[Dict[str, Any]]
    notifications: List[Dict[str, Any]]
    
    # Execution tracking
    current_step: str
    completed_steps: List[str]
    next_actions: List[str]


class InvestigationState(TypedDict):
    """State for investigation sub-graph."""
    incident_id: str
    investigator_id: str
    focus_area: str
    findings: List[InvestigationFinding]
    evidence: List[Dict[str, Any]]
    analysis_notes: List[str]
    confidence_level: float
    status: str


class AnalysisState(TypedDict):
    """State for analysis sub-graph."""
    incident_id: str
    analyst_id: str
    data_sources: List[str]
    analysis_results: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    correlations: List[Dict[str, Any]]
    insights: List[str]
    status: str


class CommunicationState(TypedDict):
    """State for communication sub-graph."""
    incident_id: str
    communicator_id: str
    stakeholders: List[str]
    messages_sent: List[Dict[str, Any]]
    messages_received: List[Dict[str, Any]]
    escalation_level: int
    communication_plan: Dict[str, Any]
    status: str


class ExecutionState(TypedDict):
    """State for execution sub-graph."""
    incident_id: str
    executor_id: str
    actions_planned: List[Dict[str, Any]]
    actions_executed: List[Dict[str, Any]]
    actions_failed: List[Dict[str, Any]]
    resources_allocated: Dict[str, Any]
    progress: float
    status: str


class CoordinatorState(TypedDict):
    """State for coordinator agent."""
    incident_id: str
    coordinator_id: str
    agent_assignments: Dict[str, str]
    workflow_status: Dict[str, str]
    decision_points: List[Dict[str, Any]]
    approvals_required: List[Dict[str, Any]]
    escalations: List[Dict[str, Any]]
    status: str


# Type aliases for better readability
IncidentContext = Dict[str, Any]
AgentContext = Dict[str, Any]
InvestigationContext = Dict[str, Any]
AnalysisContext = Dict[str, Any]
CommunicationContext = Dict[str, Any]
ExecutionContext = Dict[str, Any]

