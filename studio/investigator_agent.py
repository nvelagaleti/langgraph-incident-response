"""
Investigator Agent for LangGraph Studio.
This graph demonstrates an investigator agent that analyzes incidents and provides findings.
"""

import os
from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import uuid

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from dotenv import load_dotenv
import sys
import os

# Add parent directory to path to import Circuit LLM client
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()


# State definition
class InvestigatorState(TypedDict):
    """State for the investigator agent workflow."""
    incident_id: str
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime
    findings: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    root_cause_analysis: Dict[str, Any]
    messages: List[Dict[str, Any]]


# Circuit LLM setup
from circuit_llm_client import CircuitLLMWrapper

# Initialize Circuit LLM wrapper
circuit_llm_wrapper = CircuitLLMWrapper()

# Create a LangChain-compatible LLM interface
class CircuitLLM:
    """LangChain-compatible interface for Circuit LLM."""
    
    def __init__(self, wrapper: CircuitLLMWrapper):
        self.wrapper = wrapper
    
    async def invoke(self, input_text: str) -> str:
        """Invoke Circuit LLM with input text."""
        return await self.wrapper.invoke(input_text)
    
    async def ainvoke(self, input_text: str) -> str:
        """Async invoke Circuit LLM with input text."""
        return await self.wrapper.ainvoke(input_text)

# Initialize the LLM
llm = CircuitLLM(circuit_llm_wrapper)


async def initialize_investigation(state: InvestigatorState) -> InvestigatorState:
    """Initialize the investigation process and generate incident details."""
    print("🔍 Initializing Investigation...")
    
    incident_id = state.get('incident_id', '')
    
    # Generate incident details using Circuit LLM
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an incident response analyst. Generate realistic incident details based on the incident ID.
        Create a plausible incident scenario that could occur in a software system.
        """),
        ("human", """
        Incident ID: {incident_id}
        
        Generate incident details as JSON:
        {{
            "title": "string",
            "description": "string", 
            "severity": "critical|high|medium|low"
        }}
        """)
    ])
    
    try:
        # Format the prompt
        formatted_prompt = prompt.format_messages(incident_id=incident_id)
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            incident_details = json.loads(json_match.group())
        else:
            # Fallback
            incident_details = {
                "title": f"Incident {incident_id}",
                "description": "System performance degradation detected",
                "severity": "high"
            }
        
        updated_state = state.copy()
        updated_state.update({
            'title': incident_details.get('title', f'Incident {incident_id}'),
            'description': incident_details.get('description', ''),
            'severity': incident_details.get('severity', 'medium'),
            'status': 'INVESTIGATING',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'findings': [],
            'evidence': [],
            'root_cause_analysis': {},
            'messages': state.get('messages', []) + [{
                'role': 'system',
                'content': f'Investigator agent initialized for {incident_id}.'
            }]
        })
        
        print(f"✅ Investigation initialized: {updated_state['incident_id']}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error initializing investigation: {e}")
        return state


async def gather_evidence(state: InvestigatorState) -> InvestigatorState:
    """Gather evidence related to the incident."""
    print("📋 Gathering Evidence...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an Incident Response Investigator. Gather evidence related to the incident.
        """),
        ("human", """
        Incident: {title}
        Severity: {severity}
        Description: {description}
        
        Identify evidence to gather as JSON:
        {{
            "evidence_sources": ["list", "of", "evidence", "sources"],
            "data_points": ["list", "of", "data", "points"],
            "artifacts": ["list", "of", "artifacts"],
            "timeline_events": ["list", "of", "timeline", "events"]
        }}
        """)
    ])
    
    try:
        # Format the prompt
        formatted_prompt = prompt.format_messages(
            title=state.get('title', 'Unknown'),
            severity=state.get('severity', 'Unknown'),
            description=state.get('description', 'No description')
        )
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"evidence_sources": [], "data_points": []}
        
        updated_state = state.copy()
        updated_state.update({
            'status': 'GATHERING_EVIDENCE',
            'updated_at': datetime.now(),
            'evidence': result,
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Evidence gathered. Sources: {len(result.get('evidence_sources', []))} identified"
            }]
        })
        
        print(f"✅ Evidence gathered: {len(result.get('evidence_sources', []))} sources")
        return updated_state
        
    except Exception as e:
        print(f"❌ Evidence gathering error: {e}")
        return state


async def analyze_findings(state: InvestigatorState) -> InvestigatorState:
    """Analyze findings and evidence."""
    print("🔬 Analyzing Findings...")
    
    evidence = state.get('evidence', {})
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an Incident Response Investigator. Analyze the evidence and provide findings.
        """),
        ("human", """
        Evidence: {evidence}
        
        Provide findings as JSON:
        {{
            "findings": [
                {{
                    "title": "string",
                    "description": "string",
                    "severity": "high|medium|low",
                    "confidence": 0.0-1.0,
                    "evidence": "string"
                }}
            ],
            "patterns": ["list", "of", "patterns"],
            "anomalies": ["list", "of", "anomalies"]
        }}
        """)
    ])
    
    try:
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "evidence": str(evidence)
        })
        
        updated_state = state.copy()
        updated_state.update({
            'status': 'ANALYZING',
            'updated_at': datetime.now(),
            'findings': result.get('findings', []),
            'patterns': result.get('patterns', []),
            'anomalies': result.get('anomalies', []),
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Analysis completed. Found {len(result.get('findings', []))} findings"
            }]
        })
        
        print(f"✅ Analysis completed: {len(updated_state['findings'])} findings")
        return updated_state
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return state


async def determine_root_cause(state: InvestigatorState) -> InvestigatorState:
    """Determine the root cause of the incident."""
    print("🎯 Determining Root Cause...")
    
    findings = state.get('findings', [])
    evidence = state.get('evidence', {})
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an Incident Response Investigator. Determine the root cause based on findings and evidence.
        """),
        ("human", """
        Findings: {findings}
        Evidence: {evidence}
        
        Provide root cause analysis as JSON:
        {{
            "root_cause": "string",
            "contributing_factors": ["list", "of", "factors"],
            "confidence": 0.0-1.0,
            "evidence_supporting": "string",
            "prevention_measures": ["list", "of", "measures"]
        }}
        """)
    ])
    
    try:
        chain = prompt | llm | JsonOutputParser()
        result = chain.invoke({
            "findings": str(findings),
            "evidence": str(evidence)
        })
        
        updated_state = state.copy()
        updated_state.update({
            'status': 'ROOT_CAUSE_DETERMINED',
            'updated_at': datetime.now(),
            'root_cause_analysis': result,
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Root cause determined: {result.get('root_cause', 'Unknown')}"
            }]
        })
        
        print(f"✅ Root cause determined: {result.get('root_cause', 'Unknown')}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Root cause analysis error: {e}")
        return state


async def finalize_investigation(state: InvestigatorState) -> InvestigatorState:
    """Finalize the investigation process."""
    print("🏁 Finalizing Investigation...")
    
    updated_state = state.copy()
    updated_state.update({
        'status': 'INVESTIGATION_COMPLETE',
        'updated_at': datetime.now(),
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': 'Investigation completed successfully.'
        }]
    })
    
    print("✅ Investigation finalized")
    return updated_state


# Create the graph
def create_graph() -> StateGraph:
    """Create the investigator agent graph."""
    
    workflow = StateGraph(InvestigatorState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_investigation)
    workflow.add_node("gather_evidence", gather_evidence)
    workflow.add_node("analyze", analyze_findings)
    workflow.add_node("root_cause", determine_root_cause)
    workflow.add_node("finalize", finalize_investigation)
    
    # Define edges
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "gather_evidence")
    workflow.add_edge("gather_evidence", "analyze")
    workflow.add_edge("analyze", "root_cause")
    workflow.add_edge("root_cause", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


# Create the graph instance
graph = create_graph()
