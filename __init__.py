"""
LangGraph Incident Response System

A sophisticated multi-agent incident response system built with LangGraph,
following patterns from LangChain Academy Module 4 & 5.

Key Features:
- Multi-agent architecture with specialized roles
- Parallel execution using subgraphs
- Memory management and persistence
- State management with checkpointing
- Automated root cause analysis
"""

__version__ = "1.0.0"
__author__ = "LangGraph Incident Response Team"
__description__ = "Multi-agent incident response system with LangGraph"

from .graphs.main_graph import IncidentResponseGraph
from .types.state import (
    IncidentState,
    InvestigationState,
    AnalysisState,
    CommunicationState,
    ExecutionState,
    IncidentSeverity,
    IncidentStatus,
    AgentRole
)
from .agents.base_agent import BaseAgent, AgentFactory
from .agents.coordinator_agent import CoordinatorAgent

__all__ = [
    "IncidentResponseGraph",
    "IncidentState",
    "InvestigationState", 
    "AnalysisState",
    "CommunicationState",
    "ExecutionState",
    "IncidentSeverity",
    "IncidentStatus",
    "AgentRole",
    "BaseAgent",
    "AgentFactory",
    "CoordinatorAgent"
]

