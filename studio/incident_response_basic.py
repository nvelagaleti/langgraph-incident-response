"""
Basic Incident Response Graph for LangGraph Studio.
This graph demonstrates a simple incident response workflow without external integrations.
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
class IncidentState(TypedDict):
    """State for the basic incident response workflow."""
    incident_id: str
    title: str
    description: str
    severity: str
    status: str
    created_at: datetime
    updated_at: datetime
    findings: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    actions_taken: List[Dict[str, Any]]
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


async def initialize_incident(state: IncidentState) -> IncidentState:
    """Initialize the incident response process and generate incident details."""
    print("🚨 Initializing Basic Incident Response...")
    
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
            'status': 'INITIALIZED',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'findings': [],
            'recommendations': [],
            'actions_taken': [],
            'messages': state.get('messages', []) + [{
                'role': 'system',
                'content': f'Basic incident response system initialized for {incident_id}.'
            }]
        })
        
        print(f"✅ Incident initialized: {updated_state['incident_id']}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Error initializing incident: {e}")
        return state


async def investigate_incident(state: IncidentState) -> IncidentState:
    """Investigate the incident."""
    print("🔍 Investigating Incident...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an Incident Response Investigator. Analyze the incident and identify potential issues.
        """),
        ("human", """
        Incident: {title}
        Severity: {severity}
        Description: {description}
        
        Provide findings as JSON:
        {{
            "findings": [
                {{
                    "title": "string",
                    "description": "string",
                    "severity": "high|medium|low",
                    "confidence": 0.0-1.0
                }}
            ]
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
            result = {"findings": []}
        
        updated_state = state.copy()
        updated_state.update({
            'status': 'INVESTIGATING',
            'updated_at': datetime.now(),
            'findings': result.get('findings', []),
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Investigation completed. Found {len(result.get('findings', []))} findings."
            }]
        })
        
        print(f"✅ Investigation completed: {len(updated_state['findings'])} findings")
        return updated_state
        
    except Exception as e:
        print(f"❌ Investigation error: {e}")
        return state


async def generate_recommendations(state: IncidentState) -> IncidentState:
    """Generate recommendations based on findings."""
    print("💡 Generating Recommendations...")
    
    findings = state.get('findings', [])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an incident response analyst. Generate recommendations based on findings.
        """),
        ("human", """
        Findings: {findings}
        
        Generate recommendations as JSON:
        {{
            "recommendations": [
                {{
                    "title": "string",
                    "description": "string",
                    "priority": "high|medium|low"
                }}
            ]
        }}
        """)
    ])
    
    try:
        # Format the prompt
        formatted_prompt = prompt.format_messages(findings=str(findings))
        prompt_text = formatted_prompt[-1].content
        
        # Call Circuit LLM
        response = await llm.invoke(prompt_text)
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"recommendations": []}
        
        updated_state = state.copy()
        updated_state.update({
            'status': 'RECOMMENDING',
            'updated_at': datetime.now(),
            'recommendations': result.get('recommendations', []),
            'messages': state.get('messages', []) + [{
                'role': 'assistant',
                'content': f"Recommendations generated: {len(result.get('recommendations', []))} recommendations"
            }]
        })
        
        print(f"✅ Recommendations generated: {len(updated_state['recommendations'])}")
        return updated_state
        
    except Exception as e:
        print(f"❌ Recommendation generation error: {e}")
        return state


async def finalize_incident(state: IncidentState) -> IncidentState:
    """Finalize the incident response process."""
    print("🏁 Finalizing Incident Response...")
    
    updated_state = state.copy()
    updated_state.update({
        'status': 'RESOLVED',
        'updated_at': datetime.now(),
        'messages': state.get('messages', []) + [{
            'role': 'assistant',
            'content': 'Incident response completed successfully.'
        }]
    })
    
    print("✅ Incident finalized")
    return updated_state


# Create the graph
def create_graph() -> StateGraph:
    """Create the basic incident response graph."""
    
    workflow = StateGraph(IncidentState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_incident)
    workflow.add_node("investigate", investigate_incident)
    workflow.add_node("recommend", generate_recommendations)
    workflow.add_node("finalize", finalize_incident)
    
    # Define edges
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "investigate")
    workflow.add_edge("investigate", "recommend")
    workflow.add_edge("recommend", "finalize")
    workflow.add_edge("finalize", END)
    
    return workflow.compile()


# Create the graph instance
graph = create_graph()
